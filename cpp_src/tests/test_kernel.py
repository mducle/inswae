import pytest
import micromantid

def test_MaterialsBuilder():
   builder = micromantid.kernel.MaterialBuilder()
   mat = builder.setFormula("Li F6").setMassDensity(0.1).build()
   assert mat.numberDensity == pytest.approx(0.0034858594422501514, 0.000001)
