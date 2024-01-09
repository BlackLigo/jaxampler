# Copyright 2023 The Jaxampler Authors

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import Callable, Optional

from jax import Array, numpy as jnp
from jax.random import uniform
from tqdm import tqdm, trange

from .._rvs import ContinuousRV
from .sampler import Sampler


class MetropolisHastingSampler(Sampler):
    """Metropolis-Hasting Sampler Class"""

    def __init__(self, name: Optional[str] = None) -> None:
        super().__init__(name)

    def sample(
        self,
        p: ContinuousRV,
        q: Callable,
        burn_in: int,
        n_chains: int,
        x0: Array | tuple[Array, ...],
        *args,
        N: int = 1000,
        key: Optional[Array] = None,
        hasting_ratio: bool = False,
        **kwargs,
    ) -> Array:
        """Sample function for Metropolis-Hasting Sampler

        First, the sampler will run a burn-in phase to get the chain to
        stationarity. Then, the sampler will run the sampling phase to generate
        samples from the target distribution.

        Parameters
        ----------
        p : ContinuousRV
            Target distribution
        q : Callable[[Any], ContinuousRV], optional
            Proxy distribution, by default None
        burn_in : int, optional
            Burn-in phase, by default 100
        n_chains : int, optional
            Number of chains, by default 5
        x0 : Array, optional
            Initial values, by default None
        N : int, optional
            Number of samples, by default 1000
        key : Array, optional
            JAX PRNG key, by default None
        hasting_ratio : bool, optional
            Whether to use the Hasting ratio, by default False

        Returns
        -------
        Array
            Samples from the target distribution
        """
        x0 = jnp.asarray(x0)
        assert x0.shape == (n_chains,), f"got x0={x0}, n_chains={n_chains}"

        if hasting_ratio:
            alpha = lambda x1, x2: ((p.pdf_x(x2) / p.pdf_x(x1)) * (q(x1).pdf_x(x2) / q(x2).pdf_x(x1))).clip(0.0, 1.0)
        else:
            alpha = lambda x1, x2: (p.pdf_x(x2) / p.pdf_x(x1)).clip(0.0, 1.0)

        if key is None:
            key = self.get_key()

        x_curr = x0

        for _ in trange(
            burn_in,
            desc="Burn-in".ljust(15),
            unit="samples",
            colour="red",
            ascii=True,
            unit_scale=True,
        ):
            x_curr: Array = q(x_curr).rvs(shape=(), key=key)
            key = self.get_key(key)

        pbars = [
            tqdm(
                total=N,
                desc=f"chain {i:-6d}".ljust(15),
                unit="samples",
                position=i,
                colour="green",
                ascii=True,
                unit_scale=True,
            )
            for i in range(n_chains)
        ]

        total_pbar = tqdm(
            total=N * n_chains,
            desc="Total".ljust(15),
            unit="samples",
            position=n_chains,
            colour="blue",
            ascii=True,
            unit_scale=True,
        )

        T = jnp.zeros((n_chains,), dtype=jnp.int32)
        samples = jnp.empty((N, n_chains))

        while jnp.any(T < N):
            x_prop: Array = q(x_curr).rvs(shape=(), key=key)
            key = self.get_key(key)
            u = uniform(key, (n_chains,))
            cond = u < alpha(x_curr, x_prop)
            x_curr = jnp.where(cond, x_prop, x_curr)
            for i in range(n_chains):
                if cond[i] and T[i] < N:
                    samples = samples.at[T[i], i].set(x_prop[i])
                    pbars[i].update(1)
                    total_pbar.update(1)
            T += cond
            key = self.get_key(key)

        for i in range(n_chains):
            pbars[i].close()
        total_pbar.close()

        return samples
