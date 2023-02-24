#!/usr/bin/env python3
from __future__ import print_function
import glob
import argparse
import pickle
import csv
import os
import sys
import bisect

jimaHome= os.getenv('JIMA_HOME')

if(jimaHome is None or not os.path.isdir(jimaHome+'/src')):
   print('You must set the JIMA_HOME enviroment variable to the JIMA directory')
   print('such as "export JIMA_HOME=/home/jimaf/cgc/cgcsc/JIMA"')
   sys.exit(-1)
sys.path.append(jimaHome+'/src')

from jilLib import *
checkVersion()

import instructs
from print_jil import printInst

toolName='JIMA'
opSet=set()

def processFile(fileName):
    missing=[]
    instructs._init_()
    with open(fileName,'rb') as fn:
        jil=pickle.load(fn)


    cnt = 0

    ins = jil['ins']
    lastIdx=ins[len(ins)-1]['idx']
    funcs=jil['functions']
    secs=jil['Sections']

    addresses={}
    calls=sorted(jil['calls'].keys())
    currentCall=0
    jumps=sorted(jil['cndJumps'])
    currentJmp=0
    
    for funcId in funcs:
       addresses[funcs[funcId]['startAddr']]=funcId

    for addr in sorted(list(addresses.keys())):
       func=funcs[addresses[addr]]
       
       myCalls=[]
       while(currentCall < len(calls) and
             calls[currentCall] < func['startAddr']):
          currentCall+=1
       while(currentCall < len(calls) and
             calls[currentCall] <= func['endAddr']):       
          myCalls.append(jil['calls'][calls[currentCall]])
          currentCall +=1

       myJumpTargets=[]
       myJumps=[]
       while(currentJmp < len(jumps) and
             jumps[currentJmp] < func['startAddr']):
          currentJmp+=1
       while(currentJmp < len(jumps) and
             jumps[currentJmp] <= func['endAddr']):
          #print('Current Jmp = {:d} out of {:d}'.format(currentJmp,len(jumps)))
          myJumpTargets.append(jil['jumps'][jumps[currentJmp]])
          myJumps.append(jumps[currentJmp])          
          currentJmp +=1
       myJumps=set(myJumps)       

       '''
       print('*****************************')
       print('*')
       print('* {:18s}: {:d}'.format('Function #',func['id']))
       print('* {:18s}: {:s}'.format('In Section',secs[func['secId']]['name']))
       print('* {:18s}: 0x{:08x}'.format('Start Addr',func['startAddr']))
       print('* {:18s}: {:10,d}'.format('Start Index',func['startIndex']))
       print('* {:18s}: 0x{:08x}'.format('End Addr',func['endAddr']))
       print('* {:18s}: {:10,d}'.format('End Index',func['endIndex']))
       print('* {:18s}: {:10,d}'.format('Length',func['len']))
       props=', '.join(func['properties'])
       print('* {:18s}: {!s}'.format('Properties',props))
       if(func['startAddr'] in jil['terminals']):
          print('* Is Terminal')
       print('* {:18s}: {:10,d}'.format('Func Calls',len(myCalls)))
       print('* {:18s}: {:10,d}'.format('Unique Calls',len(set(myCalls))))
       
       print('* {:18s}: {:10,d}'.format('Cnd Jumps',len(myJumps)))
       print('* {:18s}: {:10,d}'.format('Cnd Jmp Targets',len(myJumpTargets)))
       print('*')
       print('*****************************\n')
       '''
       countPP=0
       maxP=4
       print('*****************************\n')
       print('0x{:8x}:'.format(func['startAddr']))
       for insId in range(func['startIndex'], func['endIndex']+1):
          inst=ins[insId]
          #print(instructs.is_mov(inst))
          #print(inst['args'][0].type)
          #print(inst['args'][0].base)
          #if(instructs.is_mov(inst)):
          #if(instructs.is_mov(inst) and inst['args'][0].type =='memOffsetBase'):
             #print("{!s}".format(inst))
             #print(inst['args'][0].type)
             #print(inst['args'][0].base)
          if(instructs.is_mov(inst) and inst['args'][0].type =='memOffsetBase' and (inst['args'][0].base == '%rbp' or inst['args'][0].base == '%ebp') and inst['args'][0].offset > 0):
             if(inst['args'][0].offset > maxP):
                maxP=inst['args'][0].offset
             countPP = countPP +1
             printInst(inst,jil,sys.stdout)
             #print("{!s}".format(inst))
             #print(countPP)
       print("numParms == {:d}:".format(int((maxP-4)/4)))
def main():
   global opSet
   formatter = argparse.ArgumentDefaultsHelpFormatter
   parser = argparse.ArgumentParser(description='JIMA Results Interface',
                                    formatter_class=formatter)

   parser.add_argument('file', type=str,
                         help='file name')

   args = parser.parse_args()
   fileName=args.file
   
   jilRes=processFile(fileName)
    
    
if __name__ == "__main__":
   main()
