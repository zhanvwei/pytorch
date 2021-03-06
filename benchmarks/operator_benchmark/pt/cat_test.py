from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import operator_benchmark as op_bench
import torch
import random


"""Microbenchmarks for Cat operator"""


# Configs for PT Cat operator
cat_configs_short = op_bench.config_list(
    attr_names=['sizes', 'N', 'dim'],
    attrs=[
        [(1,    1,      1), 2, 0], # noqa
        [(512,  512,    2), 2, 1], # noqa
        [(128, 1024,    2), 2, 1], # noqa
    ],
    cross_product_configs={
        'device': ['cpu', 'cuda'],
    },
    tags=['short'],
)

cat_configs_long = op_bench.config_list(
    attr_names=['sizes', 'N', 'dim'],
    attrs=[
        [(2**10,    2**10,      2), 2, 0], # noqa
        [(2**10+1,  2**10-1,    2), 2, 1], # noqa
        [(2**10,    2**10,      2), 2, 2], # noqa

        [[ lambda: random.randint(2**6, 2**7),      2**7-17,    2**6+1], # noqa
            5, 0],
        [[ 2**6+2**5,   lambda: random.randint(2**6, 2**7),     2**6], # noqa
            5, 1],
        [[ 2**7,        2**6,       lambda: random.randint(2**6, 2**7)], # noqa
            5, 2],

        [[lambda: random.randint(2**5, 2**6),       2**5,       2**6], # noqa
            50, 0],
        [[2**5,         lambda: random.randint(2**5, 2**6),     2**6], # noqa
            50, 1],
        [[2**5+1,       2**6+1,         lambda: random.randint(2**5, 2**6)], # noqa
            50, 2],
    ],
    cross_product_configs={
        'device': ['cpu', 'cuda'],
    },
    tags=['long'],
)

# There is a different codepath on CUDA for >4 dimensions
cat_configs_multidim = op_bench.config_list(
    attr_names=['sizes', 'N', 'dim'],
    attrs=[
        [(2**6,     2**5,   2**2,   2**4,   2**5), 2, 2], # noqa
        [(2**4,     2**5,   2**2,   2**4,   2**5), 8, 2], # noqa
        [(2**3+1,   2**5-1, 2**2+1, 2**4-1, 2**5+1), 17, 4], # noqa
    ],
    cross_product_configs={
        'device': ['cpu', 'cuda'],
    },
    tags=['multidim'],
)

cat_configs_manyinputs = op_bench.config_list(
    attr_names=['sizes', 'N', 'dim'],
    attrs=[
        [[lambda: random.randint(1, 10000)], 100, 0],
        [[lambda: random.randint(1, 1000)], 1000, 0],
        [[lambda: random.randint(1, 500)], 2000, 0],
        [[lambda: random.randint(1, 300)], 3000, 0],
    ],
    cross_product_configs={
        'device': ['cpu', 'cuda'],
    },
    tags=['manyinputs'],
)

class CatBenchmark(op_bench.TorchBenchmarkBase):
    def init(self, sizes, N, dim, device):
        random.seed(42)
        self.inputs = []
        for i in range(N):
            current_sizes = [old_size() if callable(old_size) else old_size
                             for old_size in sizes]
            self.inputs.append(torch.rand(current_sizes, device=device))
        self.dim = dim
        self.set_module_name('cat')

    def forward(self):
        return torch.cat(self.inputs, dim=self.dim)


op_bench.generate_pt_test(cat_configs_short +
                          cat_configs_long +
                          cat_configs_multidim +
                          cat_configs_manyinputs,
                          CatBenchmark)

if __name__ == "__main__":
    op_bench.benchmark_runner.main()
