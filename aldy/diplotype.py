# 786

# Aldy source: diplotype.py
#   This file is subject to the terms and conditions defined in
#   file 'LICENSE', which is part of this source code package.


from typing import List, Dict, Set, Tuple

import sys

from .common import *
from .gene import Gene, CNConfig
from .refiner import MinorSolution

def write_decomposition(sample: str, 
                        gene: Gene, 
                        sol_id: int, 
                        minor: MinorSolution, 
                        f) -> None:
   """
   """

   for copy, a in enumerate(minor.solution):
      ma, mi, _ = a
      mutations = set(gene.alleles[ma].func_muts) | \
                  set(gene.alleles[ma].minors[mi].neutral_muts) | \
                  set(minor.added[a] if a in minor.added else []) 
      items = []
      if len(mutations) > 0:
         for m in sorted(mutations):
            print (m.is_functional)
            items.append([sample, 
                          gene.name, 
                          sol_id, 
                          minor.diplotype, 
                          ';'.join(mi for _, mi, _ in minor.solution),
                          copy, 
                          mi,
                          m.pos, m.op, 
                          -1,
                          ['NEUTRAL', 'DISRUPTING'][bool(m.is_functional)],
                          m.aux['dbsnp'], 
                          m.aux['old'],
                          ''])
      else:
         items.append([sample, 
                       gene.name, 
                       sol_id, 
                       minor.diplotype, 
                       ';'.join(mi for _, mi, _ in minor.solution),
                       copy, 
                       mi,
                       '', '', '', '', '', '', ''])
      for it in items:
         print('\t'.join(map(str, it)), file=f)


def write_header(f) -> None:
   print('# Aldy v1.3', file=f)
   print('\t'.join('Sample Gene SolutionID Major Minor Copy Allele Location Type Coverage Effect dbSNP Code Status'.split()), file=f)


def estimate_diplotype(gene: Gene, solution: MinorSolution) -> None:
   """
   """

   del_allele = next(a for a, cn in gene.cn_configs.items() 
                     if cn.kind == CNConfig.CNConfigType.DELETION)

   # solution is the array of (major, minor) tuples
   majors = [allele_sort_key(ma)[0] for ma, _, _ in solution.solution]
   if len(majors) == 1:
      res = '*{}/*{}'.format(del_allele, *majors)
   elif len(majors) == 2:
      res = '*{}/*{}'.format(*majors)
   else:
      major_dict = collections.defaultdict(int, collections.Counter(majors))
      diplotype: Tuple[List[str], List[str]] = ([], [])
      dc = 0
      # Handle tandems (heuristic where common tandems are groupped together, 
      #                 e.g. 1, 2, 13 -> 1+13/2 if [1,13] is a common tandem)
      for ta, tb in gene.common_tandems:
         while major_dict[ta] > 0 and major_dict[tb] > 0:
            diplotype[dc % 2].extend([ta, tb])
            dc += 1
            major_dict[ta] -= 1
            major_dict[tb] -= 1
      # Handle duplicates (heuristic where duplicate alleles are grouped together,
      #                    e.g. 1, 1, 2 -> 1+1/2)
      for allele, count in major_dict.items():
         if count > 0:
            diplotype[dc % 2].extend(count * [str(allele)])
            dc += 1
      # Each diplotype should have at least one item 
      # e.g. 1, 1 -> becomes 1+1/_ due to duplicate heuristic -> fixed to 1/1
      if len(diplotype[1]) == 0:
         diplotype = (diplotype[0][:-1], [diplotype[0][-1]])
      # Second item should be longer
      if len(diplotype[0]) > len(diplotype[1]):
         diplotype = (diplotype[1], diplotype[0])
      res = '/'.join('+'.join('*{}'.format(y) for y in x) 
                     for x in diplotype)

   solution.diplotype = res
