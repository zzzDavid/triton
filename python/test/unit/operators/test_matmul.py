import itertools

import pytest
import torch

import triton
import triton.ops


@pytest.mark.parametrize(
    "BLOCK_M, BLOCK_N, BLOCK_K, SPLIT_K, NWARP, NSTAGE, M, N, K, AT, BT, DTYPE",
    itertools.chain(
        *[
            [
                # 1 warp
                (16, 16, 16, 1, 1, 2, None, None, None, AT, BT, DTYPE),
                (32, 16, 16, 1, 1, 2, None, None, None, AT, BT, DTYPE),
                (16, 32, 16, 1, 1, 2, None, None, None, AT, BT, DTYPE),
                (16, 16, 32, 1, 1, 2, None, None, None, AT, BT, DTYPE),
                (32, 16, 32, 1, 1, 2, None, None, None, AT, BT, DTYPE),
                (16, 32, 32, 1, 1, 2, None, None, None, AT, BT, DTYPE),
                (16, 16, 64, 1, 1, 2, None, None, None, AT, BT, DTYPE),
                (64, 16, 64, 1, 1, 2, None, None, None, AT, BT, DTYPE),
                (16, 64, 64, 1, 1, 2, None, None, None, AT, BT, DTYPE),
                # 2 warp
                (64, 32, 64, 1, 2, 2, None, None, None, AT, BT, DTYPE),
                (32, 64, 64, 1, 2, 2, None, None, None, AT, BT, DTYPE),
                (64, 32, 16, 1, 2, 2, None, None, None, AT, BT, DTYPE),
                (32, 64, 16, 1, 2, 2, None, None, None, AT, BT, DTYPE),
                (128, 32, 32, 1, 2, 2, None, None, None, AT, BT, DTYPE),
                (32, 128, 32, 1, 2, 2, None, None, None, AT, BT, DTYPE),
                # 4 warp
                (128, 64, 16, 1, 4, 2, None, None, None, AT, BT, DTYPE),
                (64, 128, 16, 1, 4, 2, None, None, None, AT, BT, DTYPE),
                (128, 32, 32, 1, 4, 2, None, None, None, AT, BT, DTYPE),
                (32, 128, 32, 1, 4, 2, None, None, None, AT, BT, DTYPE),
                (128, 32, 64, 1, 4, 2, None, None, None, AT, BT, DTYPE),
                (32, 128, 64, 1, 4, 2, None, None, None, AT, BT, DTYPE),
                # 8 warp
                (128, 256, 16, 1, 8, 2, None, None, None, AT, BT, DTYPE),
                (256, 128, 16, 1, 8, 2, None, None, None, AT, BT, DTYPE),
                (256, 128, 32, 1, 8, 2, None, None, None, AT, BT, DTYPE),
                # split-k
                (64, 64, 16, 2, 4, 2, None, None, None, AT, BT, DTYPE),
                (64, 64, 16, 4, 4, 2, None, None, None, AT, BT, DTYPE),
                (64, 64, 16, 8, 4, 2, None, None, None, AT, BT, DTYPE),
                # variable input
                (128, 128, 32, 1, 4, 2, 1024, 1024, 1024, AT, BT, DTYPE),
                (128, 128, 32, 1, 4, 2, 384, 128, 640, AT, BT, DTYPE),
                (128, 128, 32, 1, 4, 2, 107, 233, 256, AT, BT, DTYPE),
                (128, 128, 32, 1, 4, 2, 107, 233, 311, AT, BT, DTYPE),
            ] for DTYPE in ["float16", "bfloat16", "float32"] for AT in [False, True] for BT in [False, True]
        ],
        # n-stage
        *[
            [
                (16, 16, 16, 1, 1, STAGES, 1024, 1024, 1024, AT, BT, DTYPE),
                (64, 32, 64, 1, 2, STAGES, 1024, 1024, 1024, AT, BT, DTYPE),
                (128, 64, 16, 1, 4, STAGES, 1024, 1024, 1024, AT, BT, DTYPE),
                (256, 128, 32, 1, 8, STAGES, 1024, 1024, 1024, AT, BT, DTYPE),
                (128, 128, 32, 1, 4, STAGES, 384, 128, 640, AT, BT, DTYPE),
                # split-k
                (64, 64, 16, 8, 4, STAGES, 1024, 1024, 1024, AT, BT, DTYPE),
                (64, 64, 16, 8, 4, STAGES, 1024, 1024, 32, AT, BT, DTYPE),
            ] for DTYPE in ["float16", "bfloat16", "float32"] for AT in [False, True] for BT in [False, True] for STAGES in [2, 3, 4]
        ]
    ),
)
def test_op(BLOCK_M, BLOCK_N, BLOCK_K, SPLIT_K, NWARP, NSTAGE, M, N, K, AT, BT, DTYPE):
    capability = torch.cuda.get_device_capability()
    if capability[0] < 7:
        pytest.skip("Only test tl.dot() on devices with sm >= 70")
    if capability[0] < 8 and DTYPE == "bfloat16":
        pytest.skip("Only test bfloat16 on devices with sm >= 80")
    if DTYPE == "bfloat16" and SPLIT_K != 1:
        pytest.skip("bfloat16 matmuls don't allow split_k for now")
    torch.manual_seed(0)
    # nuke kernel decorators -- will set meta-parameters manually
    kwargs = {'BLOCK_M': BLOCK_M, 'BLOCK_N': BLOCK_N, 'BLOCK_K': BLOCK_K, 'SPLIT_K': SPLIT_K}
    pre_hook = None if SPLIT_K == 1 else lambda nargs: nargs['C'].zero_()
    configs = [triton.Config(kwargs=kwargs, num_warps=NWARP, num_stages=NSTAGE, pre_hook=pre_hook)]
    kernel = triton.ops._matmul.kernel
    kernel.configs = configs
    # kernel.run = kernel.run.run.run

    # get matrix shape
    M = BLOCK_M if M is None else M
    N = BLOCK_N if N is None else N
    K = BLOCK_K * SPLIT_K if K is None else K
    # allocate/transpose inputs
    DTYPE = {"float16": torch.float16, "bfloat16": torch.bfloat16, "float32": torch.float32}[DTYPE]
    a = .1 * torch.randn((K, M) if AT else (M, K), device="cuda", dtype=DTYPE)
    b = .1 * torch.randn((N, K) if BT else (K, N), device="cuda", dtype=DTYPE)
    a = a.t() if AT else a
    b = b.t() if BT else b
    # run test
    th_c = torch.matmul(a, b)
    try:
        tt_c = triton.ops.matmul(a, b)
        torch.testing.assert_allclose(th_c, tt_c, atol=1e-2, rtol=0)
    except triton.OutOfResources as e:
        pytest.skip(str(e))
