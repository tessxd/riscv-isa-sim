import os 
import subprocess
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt 
import numpy as np 
import pandas as pd 
import seaborn as sns
colorpalette = sns.color_palette('colorblind',n_colors=6)

# Cache Parameter Options (bytes)
cache_sizes = [262144, 524288, 1048576, 2097152, 4194304, 8388608]
cache_ways = 4
block_size = 128 #size of at least 8 
append_num = ['one','two','three','four','five']
int_num = [1,2,3,4,5]

# Data frame to store results
column_headers = ['Cache Size','Cache Ways', 'Block Size', 'Cache Sets', 'Threads','Miss Rate']
matmul_data_df = pd.DataFrame(columns= column_headers)
vvadd_data_df = pd.DataFrame(columns= column_headers)
matmul_baseline_data_df = pd.DataFrame()
vvadd_baseline_data_df = pd.DataFrame()

# Calculate the sets for all combinations 
for cache_size in cache_sizes:
    for num, thread in zip(append_num, int_num):
        blocks = cache_size / block_size  
        sets = blocks / cache_ways
        
        #run matrix multiplication 
        matmul_command = "spike --ic=16:4:64 --dc=16:4:64 --l2=%s:%s:%s -p%s riscv-tests/benchmarks/mt-matmul-%s.riscv"%(sets,cache_ways,block_size,thread,num)
        #print(command)
        matmul_result = subprocess.Popen([matmul_command], stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).communicate()

        # Save parameters and output 
        matmul_result_str = matmul_result[0]
        #print(result_str)
        matmul_miss_rate_index = matmul_result_str.find('Miss Rate:')
        #print(miss_rate_index)
        matmul_miss_rate = matmul_result_str[matmul_miss_rate_index+23:matmul_miss_rate_index+28]
        #print(miss_rate)
        matmul_results_df = pd.DataFrame([[cache_size, cache_ways, block_size, sets, thread, float(matmul_miss_rate)]], columns=column_headers)
        matmul_data_df = matmul_data_df.append(matmul_results_df, ignore_index=True)

        #run vector addition
        vvadd_command = "spike --ic=16:4:64 --dc=16:4:64 --l2=%s:%s:%s -p%s riscv-tests/benchmarks/mt-vvadd-%s.riscv"%(sets,cache_ways,block_size,thread,num)
        #print(command)
        vvadd_result = subprocess.Popen([vvadd_command], stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).communicate()

        # Save parameters and output 
        vvadd_result_str = vvadd_result[0]
        #print(result_str)
        vvadd_miss_rate_index = vvadd_result_str.find('Miss Rate:')
        #print(miss_rate_index)
        vvadd_miss_rate = vvadd_result_str[vvadd_miss_rate_index+23:vvadd_miss_rate_index+28]
        #print(miss_rate)
        vvadd_results_df = pd.DataFrame([[cache_size, cache_ways, block_size, sets, thread, float(vvadd_miss_rate)]], columns=column_headers)
        vvadd_data_df = vvadd_data_df.append(vvadd_results_df, ignore_index=True)

        #TODO: also save instruction and data cache miss rates 

#save modified spike data to csv
matmul_data_df.to_csv('mat-mult_tagged_experiment2.csv')
vvadd_data_df.to_csv('vvadd_tagged_experiment2.csv')

#read baseline data into df 
matmul_baseline_data_df = pd.read_csv('mat-mult_tagged_baseline_experiment2.csv')
vvadd_baseline_data_df = pd.read_csv('vvadd_tagged_baseline_experiment2.csv')

print(matmul_data_df)
print(vvadd_data_df)
matmul_one_df = matmul_data_df[matmul_data_df['Threads']==1]
matmul_two_df = matmul_data_df[matmul_data_df['Threads']==2]
matmul_three_df = matmul_data_df[matmul_data_df['Threads']==3]
matmul_four_df = matmul_data_df[matmul_data_df['Threads']==4]
matmul_five_df = matmul_data_df[matmul_data_df['Threads']==5]
vvadd_one_df = vvadd_data_df[vvadd_data_df['Threads']==1]
vvadd_two_df = vvadd_data_df[vvadd_data_df['Threads']==2]
vvadd_three_df = vvadd_data_df[vvadd_data_df['Threads']==3]
vvadd_four_df = vvadd_data_df[vvadd_data_df['Threads']==4]
vvadd_five_df = vvadd_data_df[vvadd_data_df['Threads']==5]

matmul_one_diff_df = matmul_data_df[matmul_data_df['Threads']==1] - matmul_baseline_data_df[matmul_baseline_data_df['Threads']==1]
matmul_two_diff_df = matmul_data_df[matmul_data_df['Threads']==2] - matmul_baseline_data_df[matmul_baseline_data_df['Threads']==2]
matmul_three_diff_df = matmul_data_df[matmul_data_df['Threads']==3] - matmul_baseline_data_df[matmul_baseline_data_df['Threads']==3]
matmul_four_diff_df = matmul_data_df[matmul_data_df['Threads']==4] - matmul_baseline_data_df[matmul_baseline_data_df['Threads']==4]
matmul_five_diff_df = matmul_data_df[matmul_data_df['Threads']==5] - matmul_baseline_data_df[matmul_baseline_data_df['Threads']==5]
vvadd_one_diff_df = vvadd_data_df[vvadd_data_df['Threads']==1] - vvadd_baseline_data_df[vvadd_baseline_data_df['Threads']==1]
vvadd_two_diff_df = vvadd_data_df[vvadd_data_df['Threads']==2] - vvadd_baseline_data_df[vvadd_baseline_data_df['Threads']==2]
vvadd_three_diff_df = vvadd_data_df[vvadd_data_df['Threads']==3] - vvadd_baseline_data_df[vvadd_baseline_data_df['Threads']==3]
vvadd_four_diff_df = vvadd_data_df[vvadd_data_df['Threads']==4] - vvadd_baseline_data_df[vvadd_baseline_data_df['Threads']==4]
vvadd_five_diff_df = vvadd_data_df[vvadd_data_df['Threads']==5] - vvadd_baseline_data_df[vvadd_baseline_data_df['Threads']==5]


#vector addition figure
fig1 = plt.figure()
plt.plot(np.log(vvadd_one_df['Cache Size'].tolist()),vvadd_one_df['Miss Rate'], color=colorpalette[0], label='1 enclave')
plt.plot(np.log(vvadd_two_df['Cache Size'].tolist()),vvadd_two_df['Miss Rate'], color=colorpalette[1], label='2 enclaves')
plt.plot(np.log(vvadd_three_df['Cache Size'].tolist()),vvadd_three_df['Miss Rate'], color=colorpalette[2], label='3 enclaves')
plt.plot(np.log(vvadd_four_df['Cache Size'].tolist()),vvadd_four_df['Miss Rate'], color=colorpalette[3], label='4 enclaves')
plt.plot(np.log(vvadd_five_df['Cache Size'].tolist()),vvadd_five_df['Miss Rate'], color=colorpalette[4], label='5 enclaves')
plt.title('Vector Addition with 4-Way L2 Cache', fontsize=16)
plt.ylabel('L2 Miss Rates (%)', fontsize=16)
plt.xlabel('Cache Size', fontsize=16)
plt.xticks(np.log(vvadd_one_df['Cache Size'].tolist()),['256KB','512KB','1MB','2MB','4MB','8MB'])
plt.yticks(np.arange(10,40,step=5))
plt.legend()
fig1.savefig('vvadd_tagged_experiment2.png')
fig1.savefig('vvadd_tagged_experiment2.pdf')
plt.close()

#vector addition difference figure 
fig2 = plt.figure()
plt.plot(np.log(vvadd_one_df['Cache Size'].tolist()),vvadd_one_diff_df['Miss Rate'], color=colorpalette[0], label='1 enclave')
plt.plot(np.log(vvadd_two_df['Cache Size'].tolist()),vvadd_two_diff_df['Miss Rate'], color=colorpalette[1], label='2 enclaves')
plt.plot(np.log(vvadd_three_df['Cache Size'].tolist()),vvadd_three_diff_df['Miss Rate'], color=colorpalette[2], label='3 enclaves')
plt.plot(np.log(vvadd_four_df['Cache Size'].tolist()),vvadd_four_diff_df['Miss Rate'], color=colorpalette[3], label='4 enclaves')
plt.plot(np.log(vvadd_five_df['Cache Size'].tolist()),vvadd_five_diff_df['Miss Rate'], color=colorpalette[4], label='5 enclaves')
plt.title('Vector Addition with 4-Way L2 Cache', fontsize=16)
plt.ylabel('L2 Miss Rates Delta (%)', fontsize=16)
plt.xlabel('Cache Size', fontsize=16)
plt.xticks(np.log(vvadd_one_df['Cache Size'].tolist()),['256KB','512KB','1MB','2MB','4MB','8MB'])
plt.yticks(np.arange(10,40,step=5))
plt.legend()
fig2.savefig('vvadd_tagged_diff_experiment2.png')
fig2.savefig('vvadd_tagged_diff_experiment2.pdf')
plt.close()

#matrix multiplication figure 
fig3 = plt.figure()
plt.plot(np.log(matmul_one_df['Cache Size'].tolist()),matmul_one_df['Miss Rate'], color=colorpalette[0], label='1 enclave')
plt.plot(np.log(matmul_two_df['Cache Size'].tolist()),matmul_two_df['Miss Rate'], color=colorpalette[1], label='2 enclaves')
plt.plot(np.log(matmul_three_df['Cache Size'].tolist()),matmul_three_df['Miss Rate'], color=colorpalette[2], label='3 enclaves')
plt.plot(np.log(matmul_four_df['Cache Size'].tolist()),matmul_four_df['Miss Rate'], color=colorpalette[3], label='4 enclaves')
plt.plot(np.log(matmul_five_df['Cache Size'].tolist()),matmul_five_df['Miss Rate'], color=colorpalette[4], label='5 enclaves')
plt.title('Matrix Multiplication with 4-Way L2 Cache', fontsize=16) 
plt.ylabel('L2 Miss Rates (%)', fontsize=16)
plt.xlabel('Cache Size', fontsize=16)
plt.xticks(np.log(matmul_one_df['Cache Size'].tolist()),['256KB','512KB','1MB','2MB','4MB','8MB'])
plt.yticks(np.arange(30,80,step=10))
plt.legend()
fig3.savefig('mat-mult_tagged_experiment2.png')
fig3.savefig('mat-mult_tagged_experiment2.pdf')
plt.close()

#matrix multiplication difference figure
fig4 = plt.figure()
plt.plot(np.log(matmul_one_df['Cache Size'].tolist()),matmul_one_diff_df['Miss Rate'], color=colorpalette[0], label='1 enclave')
plt.plot(np.log(matmul_two_df['Cache Size'].tolist()),matmul_two_diff_df['Miss Rate'], color=colorpalette[1], label='2 enclaves')
plt.plot(np.log(matmul_three_df['Cache Size'].tolist()),matmul_three_diff_df['Miss Rate'], color=colorpalette[2], label='3 enclaves')
plt.plot(np.log(matmul_four_df['Cache Size'].tolist()),matmul_four_diff_df['Miss Rate'], color=colorpalette[3], label='4 enclaves')
plt.plot(np.log(matmul_five_df['Cache Size'].tolist()),matmul_five_diff_df['Miss Rate'], color=colorpalette[4], label='5 enclaves')
plt.title('Matrix Multiplication with 4-Way L2 Cache', fontsize=16) 
plt.ylabel('L2 Miss Rates Delta (%)', fontsize=16)
plt.xlabel('Cache Size', fontsize=16)
plt.xticks(np.log(matmul_one_df['Cache Size'].tolist()),['256KB','512KB','1MB','2MB','4MB','8MB'])
plt.yticks(np.arange(10,45,step=5))
plt.legend()
fig4.savefig('mat-mult_tagged_diff_experiment2.png')
fig4.savefig('mat-mult_tagged_diff_experiment2.pdf')
plt.close()



