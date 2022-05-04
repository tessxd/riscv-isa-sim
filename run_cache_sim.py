import os 
import subprocess
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt 
import numpy as np 
import pandas as pd 

# Cache Parameter Options (bytes)
cache_sizes = [262144, 524288, 1048576, 2097152, 4194304, 8388608] # 1048576*2,  67108864, 268435456] # 1024*40, 1024*60, 1024*100, 1024*150, 1024*200, 1024*250]
ways = 4 
block_size = 128 #size of at least 8 

# Data frames to store results
column_headers = ['Cache Size','Cache Ways', 'Block Size', 'Cache Sets', 'Miss Rate']
data_bl_df = pd.DataFrame(columns= column_headers)
data_rs_df = pd.DataFrame(columns= column_headers)
data_rb_df = pd.DataFrame(columns= column_headers)

# Calculate the sets for all combinations 
for cache_size in cache_sizes:
    #BASELINE
    blocks = cache_size / (block_size) # - 4 for tag or keep blocks the same size and reduce number of sets 
    sets = blocks / ways

    # Run command for each possible combination 
    command = "spike --ic=16:4:64 --dc=16:4:64 --l2=%s:%s:%s riscv-tests/benchmarks/mt-matmul-one.riscv"%(sets,ways,block_size)
    result = subprocess.Popen([command], stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).communicate()

    # Save parameters and output 
    result_str = result[0]
    miss_rate_index = result_str.find('Miss Rate:')
    miss_rate = result_str[miss_rate_index+23:miss_rate_index+28]
    results_bl_df = pd.DataFrame([[cache_size, ways, block_size, sets, float(miss_rate)]], columns=column_headers)
    data_bl_df = data_bl_df.append(results_bl_df, ignore_index=True)

    #REDUCE SETS BY FACTOR OF 8 
    blocks = cache_size / (block_size) # - 4 for tag or keep blocks the same size and reduce number of sets 
    sets = (blocks / ways)/2

    # Run command for each possible combination 
    command = "spike --ic=16:4:64 --dc=16:4:64 --l2=%s:%s:%s riscv-tests/benchmarks/mt-matmul-one.riscv"%(sets,ways,block_size)
    result = subprocess.Popen([command], stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).communicate()

    # Save parameters and output 
    result_str = result[0]
    miss_rate_index = result_str.find('Miss Rate:')
    miss_rate = result_str[miss_rate_index+23:miss_rate_index+28]
    results_rs_df = pd.DataFrame([[cache_size, ways, block_size, sets, float(miss_rate)]], columns=column_headers)
    data_rs_df = data_rs_df.append(results_rs_df, ignore_index=True)

    #REDUCE BLOCK SIZE BY FACTOR OF 8 
    blocks = cache_size / (block_size/2) # - 4 for tag or keep blocks the same size and reduce number of sets 
    sets = (blocks / ways)

    # Run command for each possible combination 
    command = "spike --ic=16:4:64 --dc=16:4:64 --l2=%s:%s:%s riscv-tests/benchmarks/mt-matmul-one.riscv"%(sets,ways,block_size/2)
    result = subprocess.Popen([command], stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).communicate()

    # Save parameters and output 
    result_str = result[0]
    miss_rate_index = result_str.find('Miss Rate:')
    miss_rate = result_str[miss_rate_index+23:miss_rate_index+28]
    results_rb_df = pd.DataFrame([[cache_size, ways, block_size/2, sets, float(miss_rate)]], columns=column_headers)
    data_rb_df = data_rb_df.append(results_rb_df, ignore_index=True)

# TODO: plot outputs 
print("Base line results")
print data_bl_df
print("Reduce sets by factor of 2")
print data_rs_df
print("Reduce block size by factor of 2")
print data_rb_df

data = {'C':20, 'C++':15, 'Java':30,
        'Python':35, 'Pytho':35, 'Pyth':35}
Cache_size_list = ['256KB', '512KB', '1MB', '2MB', '4MB', '8MB']#list(data.keys())
values = [35.55, 35.55, 35.0, 35.0, 35.0, 35.0] #list(data.values())

print data_bl_df['Cache Size'].tolist()
print data_bl_df['Miss Rate'].tolist()

fig5 = plt.figure()
X_axis = np.arange(len(Cache_size_list))

plt.bar(X_axis - 0.25, data_bl_df['Miss Rate'].tolist(), color='b', width=0.25, label='Baseline')
plt.bar(X_axis, data_rs_df['Miss Rate'].tolist(), color='g', width=0.25, label='Reduce Block Size')
plt.bar(X_axis + 0.25, data_rb_df['Miss Rate'].tolist(), color='purple', width=0.25, label='Reduce Sets')
plt.xticks(X_axis,Cache_size_list)
plt.yticks(np.arange(0,95,step=5))
plt.legend()
plt.title('Experiment 1: L3 4-Way Area Neutral Simulation')
plt.xlabel('Cache Size')
plt.ylabel('L2 Miss Rates (%)')
fig5.savefig('figure3.pdf')
plt.close()

# plt.figure()
#ax = fig1.add_axes([0,0,1,1])
#plt.bar(data_bl_df['Cache Size'].tolist(),data_bl_df['Miss Rate'].tolist(), color='b',width=0.25)
#fig4.savefig('figure3.png')
#plt.close()




#524288, 1048576, 2097152, 4194304, 8388608
#halfMB_df = data_df[data_df['Cache Size']==524288]
#oneMB_df = data_df[data_df['Cache Size']==1048576]
#twoMB_df = data_df[data_df['Cache Size']==1048576*2]
#fourMB_df = data_df[data_df['Cache Size']==4194304]
#eightMB_df = data_df[data_df['Cache Size']==8388608]

#constantBlock_df = data_df[data_df['Block Size']==256]
#print(constantBlock_df)
#sixtyfourMB_df = data_df[data_df['Cache Size']==67108864]
#twofiftysixMB_df = data_df[data_df['Cache Size']==268435456]
#print(oneMB_df)
#print(twoMB_df)
#print(eightMB_df)
#print(sixtyfourMB_df)
#print(twofiftysixMB_df)

#fig1 = plt.figure()
#plt.plot(halfMB_df['Block Size'], halfMB_df['Miss Rate'], label='512KB Cache')
#plt.plot(oneMB_df['Block Size'],oneMB_df['Miss Rate'], label='1MB Cache')
#plt.plot(twoMB_df['Block Size'],twoMB_df['Miss Rate'], label='2MB Cache')
#plt.plot(eightMB_df['Block Size'],eightMB_df['Miss Rate'], label='8MB Cache')
#plt.plot(sixtyfourMB_df['Block Size'],sixtyfourMB_df['Miss Rate'], label='64MB Cache')
#plt.plot(twofiftysixMB_df['Block Size'],twofiftysixMB_df['Miss Rate'], label='256MB Cache')
#plt.title('Miss Rate vs. Cache Line Size')
#plt.ylabel('Miss Rate')
#plt.xlabel('Cache Line Size (bytes)')
#plt.legend()
#fig1.savefig('figure1.png')
#plt.close()


#fig2 = plt.figure()
#plt.close()


