name="$1"
cat > "test_$name.py" <<EOH
import pytest


@pytest.mark.xfail
def test_$name():
    raise NotImplementedError
EOH
