import os 
import subprocess
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt 
import numpy as np 
import pandas as pd 

# Cache Parameter Options (bytes)
cache_sizes = [1024, 2048]
cache_ways = [1] #, 2, 4, 8]
cache_lines = [32, 64, 128]
cache_blocks = [8] #size of at least 8 

# Data frame to store results
column_headers = ['Cache Size','Cache Ways','Cache Line Size', 'Block Size', 'Cache Sets', 'Miss Rate']
data_df = pd.DataFrame(columns= column_headers)

# Calculate the sets for all combinations 
for cache_size in cache_sizes:
    for line_size in cache_lines:
        for ways in cache_ways:
            for block_size in cache_blocks:
                sets = cache_size/line_size

                # Run command for each possible combination 
                #print "Sets:",sets
                #print "Ways:",ways
                #print "Block Size:",block_size
                command = "spike --ic=%s:%s:%s riscv-tests/benchmarks/median.riscv"%(sets,ways,block_size)
                result = subprocess.Popen([command], stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).communicate()

                # Save parameters and output 
                result_str = result[0]
                miss_rate_index = result_str.find('Miss Rate:')
                miss_rate = result_str[miss_rate_index+23:-2]
                results_df = pd.DataFrame([[cache_size, ways, line_size, block_size, sets, float(miss_rate)]], columns=column_headers)
                data_df = data_df.append(results_df, ignore_index=True)

# TODO: plot outputs 
print data_df
oneMB_df = data_df[data_df['Cache Size']==1024]
twoMB_df = data_df[data_df['Cache Size']==2028]

plt.plot(oneMB_df['Cache Line Size'],oneMB_df['Miss Rate'])
plt.savefig('test.png')



