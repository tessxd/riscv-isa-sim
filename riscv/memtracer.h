// See LICENSE for license details.

#ifndef _MEMTRACER_H
#define _MEMTRACER_H

#include <cstdint>
#include <string.h>
#include <vector>
#include "decode.h"

enum access_type {
  LOAD,
  STORE,
  FETCH,
};

class memtracer_t
{
 public:
  memtracer_t() {}
  virtual ~memtracer_t() {}

  virtual bool interested_in_range(uint64_t begin, uint64_t end, access_type type) = 0;
  virtual void trace(uint64_t addr, size_t bytes, access_type type, reg_t pmp) = 0;
  virtual void clean_invalidate(uint64_t addr, size_t bytes, bool clean, bool inval, reg_t pmp) = 0;
};

class memtracer_list_t : public memtracer_t
{
 public:
  bool empty() { return list.empty(); }
  bool interested_in_range(uint64_t begin, uint64_t end, access_type type)
  {
    for (auto it: list)
      if (it->interested_in_range(begin, end, type))
        return true;
    return false;
  }
  void trace(uint64_t addr, size_t bytes, access_type type, reg_t pmp)
  {
    for (auto it: list)
      it->trace(addr, bytes, type, pmp);
  }
  void clean_invalidate(uint64_t addr, size_t bytes, bool clean, bool inval, reg_t pmp)
  {
    for (auto it: list)
      it->clean_invalidate(addr, bytes, clean, inval, pmp);
  }
  void hook(memtracer_t* h)
  {
    list.push_back(h);
  }
 private:
  std::vector<memtracer_t*> list;
};

#endif
