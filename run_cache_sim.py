import os 
import subprocess
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt 
import numpy as np 
import pandas as pd 

# Cache Parameter Options (bytes)
cache_sizes = [1048576, 1048576*2] # 1024*40, 1024*60, 1024*100, 1024*150, 1024*200, 1024*250]
cache_ways = [1] #, 2, 4, 8]
cache_lines = [8, 16, 32, 64, 128, 256]
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
                command = "spike --ic=512:4:64 --dc=512:4:64 --l2=%s:%s:%s riscv-tests/benchmarks/median.riscv"%(sets,ways,block_size)
                result = subprocess.Popen([command], stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).communicate()

                # Save parameters and output 
                result_str = result[0]
                #print(result_str)
                miss_rate_index = result_str.find('Miss Rate:')
                #print(miss_rate_index)
                miss_rate = result_str[miss_rate_index+23:miss_rate_index+29]
                #print(miss_rate)
                results_df = pd.DataFrame([[cache_size, ways, line_size, block_size, sets, float(miss_rate)]], columns=column_headers)
                data_df = data_df.append(results_df, ignore_index=True)

# TODO: plot outputs 
print data_df
tenMB_df = data_df[data_df['Cache Size']==1048576]
twentyMB_df = data_df[data_df['Cache Size']==1048576*2]
print(tenMB_df)
print(twentyMB_df)

fig1 = plt.figure()
plt.plot(tenMB_df['Cache Line Size'],tenMB_df['Miss Rate'], label='1MB Cache')
plt.plot(twentyMB_df['Cache Line Size'],twentyMB_df['Miss Rate'], label='2MB Cache')
plt.title('Miss Rate vs. Cache Line Size')
plt.ylabel('Miss Rate')
plt.xlabel('Cache Line Size (bytes)')
plt.legend()
fig1.savefig('figure1.png')
plt.close()


#fig2 = plt.figure()
#plt.close()


