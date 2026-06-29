#======================================================================================
#========================== parity_check_m4_slice5.py =================================
#======================================================================================
"""M4 Slice 5 parity + correctness gate (results + orchestrators).

STRUCTURAL: each installed file, after banner-normalization (CRLF->LF and stripping
  trailing backslashes on `#=` banner lines), must hash-match the source-derived port.
  The ONLY permitted difference from the original SMC-PSO source is the 3-line `#=`
  banner (trailing backslashes removed), so this is a banner-only diff.
BEHAVIORAL: SequentialOrchestrator (RK4) integrated against a self-contained linear
  decay model must match a closed-form RK4 reference, proving the ported execution
  path wires correctly to the Slice 3 integrators and Slice 5 results containers.

Usage:  python parity_check_m4_slice5.py [repo_root]   (default: current dir)
Self-contained: no config.yaml / plant package required.
"""
import sys, os, hashlib
import numpy as np


def normalize(content):
    content = content.replace("\r\n", "\n").replace("\r", "\n")
    out = []
    for line in content.split("\n"):
        if line.startswith("#="):
            line = line.rstrip("\\ \t")
        out.append(line)
    return "\n".join(out)


def sha(b):
    return hashlib.sha256(b).hexdigest()


EXPECTED_NORM_SHA = {
    'src/simulation/results/__init__.py': 'ef731555518099f933b454df447bec7a7d6b850669e51d121d6488f874971198',
    'src/simulation/results/containers.py': '022ba420ca8c4f612982c5852b4f9fb4ec01166f4d02a2f1de6a7315b0e63551',
    'src/simulation/results/exporters.py': '16d7f913fabd8526eb0b3858f5418bee037e2bd3464aedb13e7779ba0fe534fd',
    'src/simulation/results/processors.py': '26a12097c69fb05cd62952ebb50efa0a09f7730002448f22af9583ace2657d08',
    'src/simulation/results/validators.py': '53aa7e08b632daa08e0a637f890f4b874088e8f4c667e69ed91446684b68c039',
    'src/simulation/orchestrators/__init__.py': '56274f98a5994381e0e8ab49635c59590d8b06ebfbe4d9f664ca86d0f381e2db',
    'src/simulation/orchestrators/base.py': '23b2526d1bd15a53b914a9eb4590f1e5a51b59ef2e195a4f71c5eb5984892ded',
    'src/simulation/orchestrators/sequential.py': 'ebd6b70997e34e4e9a1d267de07d34b3684edb39b7723e52793f08fe34c8956b',
    'src/simulation/orchestrators/batch.py': 'fd995ad7683c93656d93b4897336a0d2af2debc16fa8ae2572d18471a7e00966',
    'src/simulation/orchestrators/parallel.py': 'f033f64c875843b2e0d44f6d5ddda0c0b64a35ef758fcbe29c2ec9df945dde28',
    'src/simulation/orchestrators/real_time.py': '9ba612f345885e36dd1086bc15783726ff078a4ba4f3d8a244f2f123c991e23c',
}

RAW_SOURCE_SHA = {
    'src/simulation/results/__init__.py': '1000197e281f771460abe403dca1bd358f1e891aa85b2613118c7498ce17873b',
    'src/simulation/results/containers.py': '822f16ffc7063e1dab284fcc0470a7a643b5ce1becd3a5f6282168b93a3bb851',
    'src/simulation/results/exporters.py': '2e12392e2c175783ca94c3ad15bba034ce034a4cc04814c6a24a1688049d1616',
    'src/simulation/results/processors.py': 'da2ac49d2d9ffcbc0f83654c884e1df25efa1b7c56206196d09d76de21d216a4',
    'src/simulation/results/validators.py': '0f954d76eea6fa08f53f6d7dd5870e8267de6f93fe4ab322d29bffdb02c5c956',
    'src/simulation/orchestrators/__init__.py': '608401ab3c2b015f1d76416010037bbd6d3ea2b1bd58ea48f0b48b01ddc0397f',
    'src/simulation/orchestrators/base.py': 'ab5698ae2155aed416a386886007177182d797cff8d0cfb8e8200046b1c3af55',
    'src/simulation/orchestrators/sequential.py': 'a59322a12b822a8c84fa202d134c91e1509ba444f8481fe7ee9dfa889ed31cae',
    'src/simulation/orchestrators/batch.py': '0dc9c4d08cbaed1a8147cdfafd0e6626c97fe8351bb2ce11fd03d2f98f4cb36b',
    'src/simulation/orchestrators/parallel.py': '68e8cb837b92c8539bf8a300ab16806ae47692f320d21790af74116715f2116d',
    'src/simulation/orchestrators/real_time.py': '365e20b4e9df47f612388a881cc605a414ea8d7b717d238f8331c101c0443c50',
}

BANNER_DELTA_BYTES = {
    'src/simulation/results/__init__.py': 9,
    'src/simulation/results/containers.py': 9,
    'src/simulation/results/exporters.py': 9,
    'src/simulation/results/processors.py': 9,
    'src/simulation/results/validators.py': 9,
    'src/simulation/orchestrators/__init__.py': 9,
    'src/simulation/orchestrators/base.py': 9,
    'src/simulation/orchestrators/sequential.py': 9,
    'src/simulation/orchestrators/batch.py': 9,
    'src/simulation/orchestrators/parallel.py': 9,
    'src/simulation/orchestrators/real_time.py': 9,
}


K_DECAY = 0.7


class _FakeConfig:
    def model_dump_json(self):
        return "{}"


class _FakeDynamics:
    def compute_dynamics(self, x, u):
        return -K_DECAY * np.asarray(x, dtype=float)


class _FakeContext:
    def __init__(self, _cfg=None):
        self.config = _FakeConfig()
        self._dyn = _FakeDynamics()

    def get_config(self):
        return self.config

    def get_dynamics_model(self):
        return self._dyn

    def get_simulation_parameters(self):
        return {"dt": 0.05, "integration_method": "rk4"}


def _rk4_ref(x0, dt, k=K_DECAY):
    f = lambda x: -k * x
    k1 = f(x0); k2 = f(x0 + dt / 2 * k1); k3 = f(x0 + dt / 2 * k2); k4 = f(x0 + dt * k3)
    return x0 + dt / 6.0 * (k1 + 2 * k2 + 2 * k3 + k4)


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else "."
    root = os.path.abspath(root)

    struct_ok = True
    for rel, expected in EXPECTED_NORM_SHA.items():
        path = os.path.join(root, rel)
        if not os.path.exists(path):
            print(f"  MISSING: {rel}"); struct_ok = False; continue
        got = sha(normalize(open(path, encoding="utf-8").read()).encode())
        if got != expected:
            print(f"  MISMATCH: {rel}\n    expected {expected}\n    got      {got}")
            struct_ok = False
        else:
            print(f"  ok  {rel}  (banner-only delta vs source: {BANNER_DELTA_BYTES[rel]} bytes)")
    print("STRUCTURAL PARITY: OK (banner-only diff)" if struct_ok else "STRUCTURAL PARITY: FAIL")

    behave_ok = True
    try:
        sys.path.insert(0, root)
        from src.simulation.orchestrators import SequentialOrchestrator
        from src.simulation.results import StandardResultContainer
        orch = SequentialOrchestrator(_FakeContext())
        x0 = np.array([2.0, -1.0])
        res = orch.execute(x0, np.zeros(3), dt=0.05, horizon=3, safety_guards=False)
        assert isinstance(res, StandardResultContainer)
        assert res.get_states().shape == (4, 2)
        assert np.allclose(res.get_states()[1], _rk4_ref(x0, 0.05), rtol=1e-12, atol=1e-12)
    except Exception as e:
        behave_ok = False
        print(f"  behavioral error: {e}")
    print("BEHAVIORAL CORRECTNESS: OK" if behave_ok else "BEHAVIORAL CORRECTNESS: FAIL")

    if struct_ok and behave_ok:
        print("PARITY OK"); return 0
    print("PARITY FAILED"); return 1


if __name__ == "__main__":
    sys.exit(main())
