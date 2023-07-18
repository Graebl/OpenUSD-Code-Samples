import argparse
import logging
from pathlib import Path
import toml
import os
import shutil

from rstcloth import RstCloth
from md_to_rst import convertMarkdownToRst


REPO_ROOT = Path(__file__).parent
SOURCE_DIR = REPO_ROOT / "source"
BUILD_DIR = REPO_ROOT / "_build" / "usd"

logger = logging.getLogger(__name__)

def main():    

    # flush build dir 
    sub_usd_build_dir = REPO_ROOT / "_build"
    if os.path.exists(sub_usd_build_dir):
        shutil.rmtree(sub_usd_build_dir)    
    
    sub_usd_build_dir.mkdir(exist_ok=False)    
    BUILD_DIR.mkdir(exist_ok=False)    

    # each config.toml should be a sample
    for config_file in SOURCE_DIR.rglob("config.toml"):
        logger.info(f"processing: {config_file.parent.name}")
        sample_source_dir = config_file.parent
        #logger.info(f"sample_source_dir:: {sample_source_dir}")
        
        sample_output_dir = BUILD_DIR / sample_source_dir.parent.relative_to(SOURCE_DIR)  / f"{config_file.parent.name}"
        #logger.info(f"sample_output_dir:: {sample_output_dir}")
        
        # make sure category dir exists
        category_output_dir = BUILD_DIR / sample_source_dir.parent.relative_to(SOURCE_DIR)
        #logger.info(f"category_output_dir:: {category_output_dir}")
               
        if not os.path.exists(category_output_dir):
            category_output_dir.mkdir(exist_ok=False)   
            
        sample_rst_out = category_output_dir / f"{config_file.parent.name}.rst"
        #logger.info(f"sample_rst_out: {sample_rst_out}")
        with open(config_file) as f:
            content = f.read()
            config = toml.loads(content)

        sample_output_dir.mkdir(exist_ok=True)
        with open(sample_rst_out, "w") as f:
            doc = RstCloth(f)
            doc.directive("meta", 
                fields=[
                    ('description', config["metadata"]["description"]), 
                    ('keywords', ", ".join(config["metadata"]["keywords"]))
            ])
            doc.newline()
            doc.newline()
            
            with open(sample_source_dir / "header.md") as header_file:
                header_content = convertMarkdownToRst(header_file.read())
                doc._stream.write(header_content)
                doc.newline()
                doc.newline()            

            doc.directive("tab-set")
            doc.newline()           
            
            code_flavors = {"USD Python" : "py_usd.md",
                            "omni.usd Python" : "py_omni_usd.md",
                            "omni.usd C++" : "cpp_omni_usd.md",
                            "Kit Commands" : "py_kit_cmds.md",  
                            "USD C++" : "cpp_usd.md",  
                            "USDA" : "usda.md",  
            }
            
            for tab_name in code_flavors:
                md_file_name = code_flavors[tab_name]
                md_file_path = sample_source_dir / code_flavors[tab_name]
                
                if md_file_path.exists():
                    doc.directive("tab-item", tab_name, None, None, 3)
                    doc.newline()
                    
                    # make sure all md flavor names are unique
                    new_md_name = config_file.parent.name + "_" + md_file_name
                    category_output_dir

                    out_md = category_output_dir / new_md_name
                    prepend_include_path(md_file_path, out_md, config_file.parent.name)
                       
                    fields = [("parser" , "myst_parser.sphinx_")]
                    doc.directive( "include", new_md_name, fields, None, 6)
                    doc.newline()        

                # copy all samples 
                shutil.copytree(sample_source_dir, sample_output_dir, ignore=shutil.ignore_patterns('*.md', 'config.toml'), dirs_exist_ok=True )
                    
            doc.newline()    


def prepend_include_path(in_file_path: str, out_file_path: str, dir_path: str):
    with open(in_file_path) as mdf:
        md_data = mdf.read()
          
    mdf.close()    
              
    md_lines = md_data.split("\n")
    lc = 0
    for line in md_lines:        
        res =  line.find( "``` {literalinclude}")
        if res > -1:
            sp = line.split("``` {literalinclude}")
            filename = sp[1].strip()
            newl = "``` {literalinclude} " + dir_path + "/" + filename
            md_lines[lc] = newl
        lc += 1
        
    with open(out_file_path,"w") as nmdf:
        #mdf.writelines(md_lines)
        for line in md_lines:
            nmdf.writelines(line + "\n")
        nmdf.close()
    
    
    

if __name__ == "__main__":
    # Create an argument parser
    parser = argparse.ArgumentParser(description='Build rST documentation from code sample source.')

    # Add arguments
    parser.add_argument('--name', help='Specify the name')

    # Parse the arguments
    args = parser.parse_args()

    # Access the values provided for the arguments
    name = args.name
    logging.basicConfig(level=logging.INFO)
    main()