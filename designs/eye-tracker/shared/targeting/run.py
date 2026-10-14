"""Rebuild a target-driven complete assembly from an explicit species recipe."""
import argparse
from pathlib import Path
from prepare import prepare
from solve import solve
from build import build
from finish import finish
from assemble import assemble
from validate import validate

def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('recipe',type=Path);parser.add_argument('--out',type=Path,required=True);args=parser.parse_args()
 for stage in [prepare,solve]:print(stage.__name__,flush=True);stage(args.recipe,args.out)
 print('build',flush=True);build(args.out)
 for stage in [finish,assemble,validate]:print(stage.__name__,flush=True);stage(args.recipe,args.out)
if __name__=='__main__':main()
