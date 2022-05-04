// See LICENSE for license details.

#include "cachesim.h"
#include "common.h"
#include <cstdlib>
#include <iostream>
#include <iomanip>

cache_sim_t::cache_sim_t(size_t _sets, size_t _ways, size_t _linesz, const char* _name)
: sets(_sets), ways(_ways), linesz(_linesz), name(_name), log(false)
{
  init();
}

static void help()
{
  std::cerr << "Cache configurations must be of the form" << std::endl;
  std::cerr << "  sets:ways:blocksize" << std::endl;
  std::cerr << "where sets, ways, and blocksize are positive integers, with" << std::endl;
  std::cerr << "sets and blocksize both powers of two and blocksize at least 8." << std::endl;
  exit(1);
}

cache_sim_t* cache_sim_t::construct(const char* config, const char* name)
{
  const char* wp = strchr(config, ':');
  if (!wp++) help();
  const char* bp = strchr(wp, ':');
  if (!bp++) help();

  size_t sets = atoi(std::string(config, wp).c_str());
  size_t ways = atoi(std::string(wp, bp).c_str());
  size_t linesz = atoi(bp);

  if (ways > 4 /* empirical */ && sets == 1)
    return new fa_cache_sim_t(ways, linesz, name);
  return new cache_sim_t(sets, ways, linesz, name);
}

void cache_sim_t::init()
{
  if(sets == 0 || (sets & (sets-1)))
    help();
  if(linesz < 8 || (linesz & (linesz-1)))
    help();

  idx_shift = 0;
  for (size_t x = linesz; x>1; x >>= 1)
    idx_shift++;

  tags = new uint64_t[sets*ways]();
  pmp_tags = new uint64_t[sets*ways]();
  read_accesses = 0;
  read_misses = 0;
  bytes_read = 0;
  write_accesses = 0;
  write_misses = 0;
  bytes_written = 0;
  writebacks = 0;

  miss_handler = NULL;
}

cache_sim_t::cache_sim_t(const cache_sim_t& rhs)
 : sets(rhs.sets), ways(rhs.ways), linesz(rhs.linesz),
   idx_shift(rhs.idx_shift), name(rhs.name), log(false)
{
  tags = new uint64_t[sets*ways];
  pmp_tags = new uint64_t[sets*ways]; 
  memcpy(tags, rhs.tags, sets*ways*sizeof(uint64_t));
  memcpy(pmp_tags, rhs.pmp_tags, sets*ways*sizeof(uint64_t));
}

cache_sim_t::~cache_sim_t()
{
  print_stats();
  delete [] pmp_tags;
  delete [] tags;
}

void cache_sim_t::print_stats()
{
  if(read_accesses + write_accesses == 0)
    return;

  float mr = 100.0f*(read_misses+write_misses)/(read_accesses+write_accesses);

  std::cout << std::setprecision(3) << std::fixed;
  std::cout << name << " ";
  std::cout << "Bytes Read:            " << bytes_read << std::endl;
  std::cout << name << " ";
  std::cout << "Bytes Written:         " << bytes_written << std::endl;
  std::cout << name << " ";
  std::cout << "Read Accesses:         " << read_accesses << std::endl;
  std::cout << name << " ";
  std::cout << "Write Accesses:        " << write_accesses << std::endl;
  std::cout << name << " ";
  std::cout << "Read Misses:           " << read_misses << std::endl;
  std::cout << name << " ";
  std::cout << "Write Misses:          " << write_misses << std::endl;
  std::cout << name << " ";
  std::cout << "Writebacks:            " << writebacks << std::endl;
  std::cout << name << " ";
  std::cout << "Miss Rate:             " << mr << '%' << std::endl;
}

//TODO: update to check pmp tag whatever thread is also of the same pmp,
// pass into simulator which enclave is running
// tag comes from address we're accessing, but we need tag from thread that we're running
// csr_write(sstatus, csr_read(sstatus) | 0x6000);

uint64_t* cache_sim_t::check_tag(uint64_t addr, reg_t pmp, std::string name)
{
  size_t idx = (addr >> idx_shift) & (sets-1);
  size_t tag = (addr >> idx_shift) | VALID;

  //std::cout << "check tag pmp " << pmp << "\n";
   //DEBUG magic number
  // if (pmp == curr_core) 
    //std::cout << "passed pmp check" << "\n";
  //if (pmp != curr_core && name == "L2$") { //pmp check to make sure pmp matches current core
  //  std::cout << "failed pmp check" << "\n";
  //  return NULL;
  //}

  //current core need to be the pmp tag that is stored 
  if (pmp == 1) {
    std::cout << "idx: " << idx << "tag: " << tag << "\n";
  }
  for (size_t i = 0; i < ways; i++) {
    //std::cout << "idx: "<< idx << "; way: " << i << "\n";
    //std::cout << "name " << name << "; pmp " << pmp << "; pmp_tag output " << pmp_tags[idx*ways + i] << "\n";
    if ((name == "L2$") && (pmp != pmp_tags[idx*ways + i]))
      continue;
    if (tag == (tags[idx*ways + i] & ~DIRTY) )  
      return &tags[idx*ways + i];
  }

  std::cout << "pmp at miss " << pmp << "\n";
  return NULL;
}
 
uint64_t cache_sim_t::victimize(uint64_t addr, reg_t pmp)
{
  size_t idx = (addr >> idx_shift) & (sets-1);
  size_t way = lfsr.next() % ways;
  uint64_t victim = tags[idx*ways + way];
  tags[idx*ways + way] = (addr >> idx_shift) | VALID;
  pmp_tags[idx*ways + way] = pmp; 
  //std::cout << "pmp: " << pmp << "; idx: "<< idx << "; way: " << way << "\n";
  return victim;
}

void cache_sim_t::access(uint64_t addr, size_t bytes, bool store, reg_t pmp)
{
  store ? write_accesses++ : read_accesses++;
  (store ? bytes_written : bytes_read) += bytes;

  uint64_t* hit_way = check_tag(addr, pmp, name);
  if (likely(hit_way != NULL))
  {
    if (store)
      *hit_way |= DIRTY;
    return;
  }

  //std::cout << name << "\n";

  store ? write_misses++ : read_misses++;
  if (log)
  {
    std::cerr << name << " "
              << (store ? "write" : "read") << " miss 0x"
              << std::hex << addr << std::endl;
  } 
  
  uint64_t victim = victimize(addr, pmp);

  if ((victim & (VALID | DIRTY)) == (VALID | DIRTY))
  {
    uint64_t dirty_addr = (victim & ~(VALID | DIRTY)) << idx_shift;
    if (miss_handler)
      miss_handler->access(dirty_addr, linesz, true, pmp);
    writebacks++;
  }

  if (miss_handler)
    miss_handler->access(addr & ~(linesz-1), linesz, false, pmp);

  if (pmp == 1 && store)
    std::cout << "testing this" << "\n";
 
  if (store) 
    *check_tag(addr, pmp, name) |= DIRTY;
}

void cache_sim_t::clean_invalidate(uint64_t addr, size_t bytes, bool clean, bool inval, reg_t pmp)
{
  uint64_t start_addr = addr & ~(linesz-1);
  uint64_t end_addr = (addr + bytes + linesz-1) & ~(linesz-1);
  uint64_t cur_addr = start_addr;
  while (cur_addr < end_addr) {
    uint64_t* hit_way = check_tag(cur_addr, pmp, name);
    if (likely(hit_way != NULL))
    {
      if (clean) {
        if (*hit_way & DIRTY) {
          writebacks++;
          *hit_way &= ~DIRTY;
        }
      }

      if (inval)
        *hit_way &= ~VALID;
    }
    cur_addr += linesz;
  }
  if (miss_handler)
    miss_handler->clean_invalidate(addr, bytes, clean, inval, pmp);
}


//TODO: make sure these are never used functions in our simulation
fa_cache_sim_t::fa_cache_sim_t(size_t ways, size_t linesz, const char* name)
  : cache_sim_t(1, ways, linesz, name)
{
}

uint64_t* fa_cache_sim_t::check_tag(uint64_t addr, reg_t pmp)
{
  auto it = tags.find(addr >> idx_shift);
  return it == tags.end() ? NULL : &it->second;
}

uint64_t fa_cache_sim_t::victimize(uint64_t addr)
{
  uint64_t old_tag = 0;
  if (tags.size() == ways)
  {
    auto it = tags.begin();
    std::advance(it, lfsr.next() % ways);
    old_tag = it->second;
    tags.erase(it);
  }
  tags[addr >> idx_shift] = (addr >> idx_shift) | VALID;
  return old_tag;
}
