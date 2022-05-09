import os 
import subprocess
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt 
import numpy as np 
import pandas as pd 
import seaborn as sns
colorpalette = sns.color_palette('colorblind',n_colors=6)
#from matplotlib.colors import ListedColormap

# Cache Parameter Options (bytes)
cache_sizes = [262144, 524288, 1048576, 2097152, 4194304, 8388608]
cache_ways = 4
block_size = 128 #size of at least 8 
append_num = ['one','two','three','four','five']
int_num = [1,2,3,4,5]

# Data frame to store results
column_headers = ['Cache Size','Cache Ways', 'Block Size', 'Cache Sets', 'Threads','Miss Rate']
data_df = pd.DataFrame(columns= column_headers)

# Calculate the sets for all combinations 
for cache_size in cache_sizes:
    for num, thread in zip(append_num, int_num):
        blocks = cache_size / block_size  
        sets = blocks / cache_ways
        
        command = "spike --ic=16:4:64 --dc=16:4:64 --l2=%s:%s:%s -p%s riscv-tests/benchmarks/mt-vvadd-%s.riscv"%(sets,cache_ways,block_size,thread,num)
        #print(command)
        result = subprocess.Popen([command], stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).communicate()

        # Save parameters and output 
        result_str = result[0]
        #print(result_str)
        miss_rate_index = result_str.find('Miss Rate:')
        #print(miss_rate_index)
        miss_rate = result_str[miss_rate_index+23:miss_rate_index+28]
        #print(miss_rate)
        results_df = pd.DataFrame([[cache_size, cache_ways, block_size, sets, thread, float(miss_rate)]], columns=column_headers)
        data_df = data_df.append(results_df, ignore_index=True)

print(data_df)
one_df = data_df[data_df['Threads']==1]
two_df = data_df[data_df['Threads']==2]
three_df = data_df[data_df['Threads']==3]
four_df = data_df[data_df['Threads']==4]
five_df = data_df[data_df['Threads']==5]
print(one_df)
print(two_df)
print(three_df)
print(four_df)
print(five_df)

#data_df.to_csv('tagged_cache_data_cleancode.csv')

#with plt.style.context(("seaborn-colorblind",)):
fig2 = plt.figure()
print(two_df['Cache Size'])
plt.plot(np.log(one_df['Cache Size'].tolist()),one_df['Miss Rate'], color=colorpalette[0], label='1 enclave')
plt.plot(np.log(two_df['Cache Size'].tolist()),two_df['Miss Rate'], color=colorpalette[1], label='2 enclaves')
plt.plot(np.log(three_df['Cache Size'].tolist()),three_df['Miss Rate'], color=colorpalette[2], label='3 enclaves')
plt.plot(np.log(four_df['Cache Size'].tolist()),four_df['Miss Rate'], color=colorpalette[3], label='4 enclaves')
plt.plot(np.log(five_df['Cache Size'].tolist()),five_df['Miss Rate'], color=colorpalette[4], label='5 enclaves')

#plt.title('4-Way LLC Multi-Threaded Vector Addition')
#plt.title('4-Way LLC Multi-Threaded Matrix Multiplication')
plt.title('Vector Addition with 4-Way L2 Cache', fontsize=16) 
#plt.title('Matrix Multiplication with 4-Way L2 Cache', fontsize=16)

plt.ylabel('L2 Miss Rates (%)', fontsize=16)
plt.xlabel('Cache Size', fontsize=16)
plt.xticks(np.log(one_df['Cache Size'].tolist()),['256KB','512KB','1MB','2MB','4MB','8MB'])
plt.yticks(np.arange(10,40,step=5))
#plt.yticks(np.arange(30,80,step=10))
plt.legend()
fig2.savefig('vvadd-tagged_experiment2.pdf')
#fig2.savefig('mat-mult_experiment2.pdf')
plt.close()

