"""Before/after coverage counts at variable/unit grain, not equivalence claims."""
from collections import defaultdict
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def profile(seed):
    records={r['id']:r for r in seed['records']};groups=defaultdict(lambda:dict(records=set(),locations=set(),series=0,values=0))
    for s in seed['series']:
        name=s.get('parameter_name_pangaea') or s.get('comparison_parameter_name')
        if not name:continue
        g=groups[(name,s['unit'])]
        if not any(row[0] is not None for row in s['rows']):continue
        r=records[s['record_id']];g['records'].add(r['id']);g['locations'].add((r['latitude'],r['longitude']))
        g['series']+=1;g['values']+=len(s['rows'])
    return {key:{**value,'records':len(value['records']),'locations':len(value['locations'])} for key,value in groups.items()}


if __name__=='__main__':
    before=json.loads((ROOT/'data/processed/atlas-v5.json').read_text(encoding='utf8'))
    after=json.loads((ROOT/'data/processed/atlas-v6.json').read_text(encoding='utf8'))
    a,b=profile(before),profile(after);changes=[]
    for (name,unit),value in b.items():
        old=a.get((name,unit),dict(records=0,locations=0,series=0,values=0))
        if value['values']>old['values']:
            changes.append(dict(parameter=name,unit=unit,before=old,after=value))
    changes.sort(key=lambda c:(-c['after']['locations'],-c['after']['records'],c['parameter'],c['unit']))
    ids={s['id'] for s in before['series']};new=[s for s in after['series'] if s['id'] not in ids]
    counts=dict(records_added=len(after['records'])-len(before['records']),series_added=len(new),observations_added=sum(len(s['rows']) for s in new))
    result=dict(parent_version=before['version'],version=after['version'],counts=counts,changes=changes,
        limitations=['Grain=controlled variable or explicit NOAA mapping + unit, not a declaration of methodological equivalence',
                    'Fractions, matrices and pollen denominators remain separated by the web comparison contexts',
                    'Coincident coordinates count once as a location, without asserting identity of different cores',
                    'Native counts are not converted to percentages or inferred forest types'])
    (ROOT/'reports/priority_v6_coverage.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps(counts))
    wanted={'Titanium/Calcium ratio','Iron/Aluminium ratio','Manganese/Aluminium ratio','Zirconium/Aluminium ratio','Zirconium/Rubidium ratio',
            'Median, grain size, D50','Arboreal pollen','Pollen, temperate','Pinus','Fagus','Size fraction 0.063-0.010 mm, sortable silt'}
    for c in changes:
        if c['parameter'] in wanted:print(c['parameter'],c['unit'],c['before']['records'],c['after']['records'],'locations',c['before']['locations'],c['after']['locations'])
