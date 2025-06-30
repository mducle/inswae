const fs = require('fs');
const fetch = require('node-fetch');

const prefix = 'https://github.com/mantidproject/mantid/raw/';
const SHA = 'a8f64cccc781eac9892433e956bab7104ebf1213';
const inst_srcpath = 'refs/heads/main/instrument';
const inst_destpath = 'py_src/mantid_instruments';
const files = {
  '/qt/python/mantidqtinterfaces/': {
    'mantidqtinterfaces/DGSPlanner/': 
      ['__init__.py', 'LoadNexusUB.py', 'MatrixUBInputWidget.py', 'ValidateOL.py', 'InstrumentSetupWidget.py', 
       'DimensionSelectorWidget.py', 'ClassicUBInputWidget.py', 'DGSPlannerGUI.py'],
    'mantidqtinterfaces/PyChop/': ['__init__.py', 'PyChopGui.py'],
    'mantidqtinterfaces/QECoverage/': ['__init__.py', 'QECoverageGUI.py'],
    'mantidqtinterfaces/SampleTransmissionCalculator/': 
      ['SampleTransmission.ui', '__init__.py', 'stc_gui.py', 'stc_model.py', 'stc_presenter.py', 'stc_view.py'],
    'mantidqtinterfaces/TofConverter/': ['__init__.py', 'convertUnits.py', 'converter.ui', 'converterGUI.py'],
  },
  '/scripts/': {
    'pychop/': 
      ['__init__.py', 'Chop.py', 'ISISDisk.py', 'ISISFermi.py', 'Instruments.py', 'MulpyRep.py',
       'arcs.yaml', 'cncs.yaml', 'hyspec.yaml', 'let.yaml', 'maps.yaml', 'mari.yaml', 'merlin.yaml', 'sequoia.yaml'],
  },
  '/Framework/PythonInterface/': {
    'mantid/plots/': ['axesfunctions.py', 'datafunctions.py', 'mantidimage.py', 'quad_mesh_wrapper.py', 'utility.py'],
    'mantid/plots/resampling_image/': ['__init__.py', 'samplingimage.py'],
    'mantid/plots/modest_image/': ['LICENSE', '__init__.py', 'modest_image.py'],
  }
};

Object.entries(files).map(
  ([rootdir, v0], i) => {
    Object.entries(v0).map(
      ([moddir, filelist], j) => {
        filelist.map(
          (filename, k) => {
            const outfile = 'mantid/' + moddir + filename;
            if(!fs.existsSync('mantid/' + moddir)) {
              fs.mkdirSync('mantid/' + moddir, { recursive: true });
            }
            if(!fs.existsSync(outfile)) {
              const fileurl = prefix + SHA + rootdir + moddir + filename;
              console.log(fileurl);
              fetch(fileurl)
                .then(response => response.text())
                .then(body => fs.writeFileSync(outfile, body));
            }
          }       
        );
      }
    );
  }
);

if(!fs.existsSync(inst_destpath)) {
  fs.mkdirSync(inst_destpath, { recursive: true });
}
[
  'ARCS_Definition_20121011-.xml', 'ARCS_Parameters.xml',
  'CHESS_Definition.xml', 'CHESS_Parameters.xml',
  'CNCS_Definition.xml', 'CNCS_Parameters.xml',
  'DNS_Definition_PAonly.xml', 'DNS_Parameters.xml', 'DNS-PSD_Definition.xml',
  'EXED_Definition.xml',
  'FOCUS_Definition.xml',
  'HB3A_Definition.xml',
  'HET_Definition.xml', 'HET_Parameters.xml',
  'HYSPEC_Definition.xml', 'HYSPEC_Parameters.xml',
  'LET_Definition.xml', 'LET_Parameters.xml',
  'MAPS_Definition.xml', 'MAPS_Parameters.xml',
  'MARI_Definition.xml', 'MARI_Parameters.xml',
  'MERLIN_Definition.xml', 'MERLIN_Parameters.xml',
  'SEQUOIA_Definition.xml', 'SEQUOIA_Parameters.xml',
  'WAND_Definition.xml', 'WAND_Parameters.xml',
].map(
  filename => {
    const outfile = inst_destpath + '/' + filename;
    if(!fs.existsSync(outfile)) {
      const fileurl = prefix + inst_srcpath + '/' + filename;
      console.log(fileurl);
      fetch(fileurl)
        .then(response => response.text())
        .then(body => fs.writeFileSync(outfile, body));
    }
  }
);
