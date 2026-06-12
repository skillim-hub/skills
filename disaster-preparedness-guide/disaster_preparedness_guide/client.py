#!/usr/bin/env python3
from __future__ import annotations
import argparse, asyncio, json, os, hashlib
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import Any, Iterable, Literal, Optional

HazardKey = Literal['missile','hostile_aircraft','earthquake','tsunami','hazmat','radiological','terrorist_infiltration','all_clear','pre_alert']

@dataclass(frozen=True)
class Protocol:
    key: HazardKey
    title_en: str
    title_he: str
    summary: str
    immediate_actions: tuple[str, ...]
    do_not: tuple[str, ...]
    shelter_time: str
    emergency_numbers: tuple[str, ...] = ()
    edge_cases: tuple[str, ...] = ()
    business_notes: tuple[str, ...] = ()
    official_override: bool = True
    plan_id: Optional[str] = None
    environment: str = 'sandbox'
    created_at: Optional[str] = None
    def to_dict(self) -> dict[str, Any]: return asdict(self)

@dataclass(frozen=True)
class HouseholdProfile:
    city: str
    people: int
    protected_space: str = 'mamad'
    pets: bool = False
    children: int = 0
    older_adults: int = 0
    accessibility_needs: bool = False
    near_coast: bool = False
    medications: bool = False

@dataclass(frozen=True)
class BusinessProfile:
    city: str
    business_type: str
    employees: int
    customers_peak: int = 0
    protected_space_capacity: Optional[int] = None
    stores_chemicals: bool = False
    uses_gas: bool = False
    keeps_customer_property: bool = False
    accessibility_needs: bool = False
    daily_revenue_nis: Optional[int] = None

@dataclass(frozen=True)
class Plan:
    plan_type: str
    title: str
    priority_actions: tuple[str, ...]
    supplies: tuple[str, ...]
    records: tuple[str, ...]
    review_cadence: str
    risk_flags: tuple[str, ...] = ()
    official_override: bool = True
    plan_id: Optional[str] = None
    environment: str = 'sandbox'
    created_at: Optional[str] = None
    def to_dict(self) -> dict[str, Any]: return asdict(self)

class UnknownHazardError(ValueError): pass

PROTOCOLS: dict[HazardKey, Protocol] = {
'missile': Protocol('missile','Rocket or missile alert','ירי רקטות וטילים','Enter the nearest protected space in time, close openings, sit low, and wait for hazard-specific official release.',('Enter mamad, mamak, miklat, stairwell, or safest interior room reachable in time.','Close protected-space door and window/shutter for missile or rocket alerts.','Sit below window line against an internal wall and protect head and neck.','If outside, lie face down away from vehicles and glass.','If driving, stop safely; exit and lie down if safe, otherwise lower below window line.'),('Do not film from windows or balconies.','Do not leave only because it is quiet.','Do not assume every long-range ballistic threat ends after 10 minutes.'),'Short-range rocket fire often uses about 10 minutes unless instructed otherwise; long-range ballistic threats require explicit official release.',('104 Home Front Command','101 MDA','102 Fire','100 Police'),('Top-floor apartment: use internal stairwell if reachable.','Store with customers: life safety overrides payment and merchandise.'),('Assign a shift lead.','Record closure time, canceled orders, and ₪ impact.')),
'hostile_aircraft': Protocol('hostile_aircraft','Hostile aircraft or drone intrusion','חדירת כלי טיס עוין','Enter protected space, close openings, avoid windows, and wait 10 minutes unless another alert or explicit official instruction is received.',('Enter protected space immediately.','Close doors and windows.','Stay away from exterior walls and glass.','Wait at least 10 minutes, unless another alert or an explicit Home Front Command instruction is received.'),('Do not go outside to look for drones.','Do not approach crash sites or suspicious objects.'),'10 minutes unless another alert is received or Home Front Command gives different explicit instructions.',('100 Police','101 MDA'),('A hostile aircraft may cross several alert areas; do not leave early to look for it.',)),
'earthquake': Protocol('earthquake','Earthquake','רעידת אדמה','Prefer open ground within seconds; otherwise stairwell or mamad with door open; otherwise Drop-Cover-Hold.',('Exit to open ground within seconds if possible.','If exit is not possible, use an internal stairwell or mamad as fallback.','Keep mamad door and window open during shaking.','If no safer option is reachable, Drop-Cover-Hold.','After shaking, avoid elevators and evacuate damaged structures.'),('Do not close or seal the mamad during an earthquake.','Do not use elevators.','Do not re-enter a damaged building until cleared.','Do not operate switches if gas is smelled.'),'Until shaking stops, then move away from damaged structures and expect aftershocks.',('102 Fire','101 MDA','106 Municipality'),('Coastal areas: watch for tsunami instructions.','Vehicle: stop away from bridges/buildings and stay belted until shaking stops.'),('Secure shelves/equipment before events.','Restart only after structure and utilities are checked.')),
'hazmat': Protocol('hazmat','Hazardous-materials or chemical incident','חומרים מסוכנים','Move indoors, usually upward, close ventilation, and avoid basements unless officials instruct otherwise.',('Enter the nearest building.','Move to an upper floor if a chemical plume may be heavier than air.','Close windows, doors, and outside-air ventilation.','Seal gaps if instructed.','If exposed, remove outer clothing carefully, bag it, and rinse skin gently.'),('Do not go to a basement for chemical plumes unless officially instructed.','Do not mix cleaning chemicals.','Do not clean unknown residue without trained guidance.','Do not eat food exposed outdoors until cleared.'),'Until fire/hazmat authorities or official channels clear the area.',('102 Fire and Rescue','101 MDA','100 Police'),('If outside, move upwind and uphill.','In a vehicle, close ventilation and leave plume area if safe.'),('Maintain chemical inventory and safety data sheets where applicable.','Document contaminated stock with photos and ₪ values only when safe.')),
'tsunami': Protocol('tsunami','Tsunami risk','צונאמי','Move inland and upward after official tsunami alert or natural warning signs near the coast.',('Move at least 1 km inland when possible.','Move to higher ground.','If trapped near the coast, go to 4th floor or higher of a sturdy building.','Leave buildings of three floors or fewer near shoreline.','Stay away from beaches, ports, marinas, river mouths, and promenades.'),('Do not return to shore to watch the sea.','Do not assume the first wave is the last or largest.'),'Remain inland or at height until official all-clear.',('104 Home Front Command','100 Police','101 MDA')),
'radiological': Protocol('radiological','Radiological event','אירוע רדיולוגי','Follow official radiological instructions; do not improvise cleanup, medication, or departure rules.',('Follow Home Front Command, police, fire-and-rescue, MDA, Ministry of Health, and local-authority instructions.','If instructed to shelter indoors, move to the directed room and close openings and outside-air ventilation.','If direct contamination is suspected, avoid spreading it and wait for emergency or medical instructions.'),('Do not take iodine tablets or medications unless officially or medically instructed.','Do not improvise decontamination, disposal, or cleanup instructions.','Do not leave shelter until official instructions change.'),'Until official radiation-safety guidance changes.',('104 Home Front Command','101 MDA','102 Fire/Rescue')),
'terrorist_infiltration': Protocol('terrorist_infiltration','Terrorist infiltration or active security incident','חדירת מחבלים','Lock, hide, silence, stay away from openings, and wait for identified security forces or official clearance.',('Enter a building or interior room.','Lock doors and windows.','Silence phones and stay quiet.','Move away from doors, windows, and exterior walls.','Call 100 when safe with location, people present, threat direction, and injuries.'),('Do not open the door to unidentified people.','Do not publish live security-force locations.','Do not leave hiding because of rumors.'),'Until identified security forces or official instructions clear the area.',('100 Police','101 MDA')),
'all_clear': Protocol('all_clear','Event concluded / all clear','האירוע הסתיים','Exit only after the relevant official release and check surroundings before resuming activity.',('Check for injuries.','Look for glass, fire, gas smell, fragments, or structural damage.','Resume only if site is safe.'),('Do not touch suspicious fragments or debris.',),'This is the release state; continue to follow official restrictions.',('100 Police','101 MDA','102 Fire')),
'pre_alert': Protocol('pre_alert','Pre-alert or early warning','התרעה מוקדמת','Prepare to enter protected space, gather people, and reduce avoidable delay.',('Move closer to protected space.','Gather children, older adults, people needing assistance, and pets.','Pause risky work, machinery, cooking, and customer service if escalation is likely.'),('Do not treat pre-alert as permission to ignore the next siren.',),'Until escalation, cancellation, or official instructions.',('104 Home Front Command',)),
}
KEYWORDS={'missile':'missile','missiles':'missile','rocket':'missile','rockets':'missile','ירי':'missile','טילים':'missile','רקטות':'missile','aircraft':'hostile_aircraft','drone':'hostile_aircraft','uav':'hostile_aircraft','כלי טיס':'hostile_aircraft','כטבם':'hostile_aircraft','כטב״ם':'hostile_aircraft','earthquake':'earthquake','quake':'earthquake','רעידת אדמה':'earthquake','רעידה':'earthquake','hazmat':'hazmat','chemical':'hazmat','חומרים מסוכנים':'hazmat','כימי':'hazmat','tsunami':'tsunami','צונאמי':'tsunami','radiological':'radiological','radiation':'radiological','nuclear':'radiological','רדיולוגי':'radiological','גרעיני':'radiological','terrorist':'terrorist_infiltration','infiltration':'terrorist_infiltration','חדירת מחבלים':'terrorist_infiltration','מחבלים':'terrorist_infiltration','all clear':'all_clear','concluded':'all_clear','הסתיים':'all_clear','pre-alert':'pre_alert','prealert':'pre_alert','warning':'pre_alert','מוקדמת':'pre_alert'}
CATEGORY_MAP={1:'missile',2:'hostile_aircraft',3:'earthquake',4:'tsunami',5:'radiological',6:'hazmat',7:'terrorist_infiltration',13:'all_clear',14:'pre_alert'}

def _norm(q: str|int)->str: return str(q).strip().casefold()

class _BasePreparednessClient:
    def __init__(self, protocols: Optional[dict[HazardKey, Protocol]]=None)->None: self.protocols=protocols or PROTOCOLS
    def list_hazards(self)->list[HazardKey]: return list(self.protocols.keys())
    def lookup(self, query: str|int)->Protocol:
        n=_norm(query)
        if n.isdigit() and int(n) in CATEGORY_MAP: return self.protocols[CATEGORY_MAP[int(n)]]
        for k,v in KEYWORDS.items():
            if k.casefold() in n: return self.protocols[v]
        if n in self.protocols: return self.protocols[n]  # type: ignore[index]
        raise UnknownHazardError(f'Unknown hazard: {query!r}')
    async def async_lookup(self, query: str|int)->Protocol: return await asyncio.to_thread(self.lookup, query)
    def decide_action(self, event_type: str|int, context: Optional[dict[str,Any]]=None)->dict[str,Any]:
        p=self.lookup(event_type); c=context or {}; actions=list(p.immediate_actions); flags=[]
        if p.key=='earthquake':
            if c.get('has_mamad'): flags.append('earthquake_mamad_door_open')
            if c.get('near_coast'): actions.append('After shaking stops, watch for tsunami signs and official alerts.')
            if c.get('can_exit_in_seconds'): actions.insert(0,'Exit to open ground immediately if safe.')
        if p.key=='hazmat' and c.get('in_basement'):
            flags.append('basement_may_be_unsafe_for_chemical_plume'); actions.insert(0,'Leave basement for an upper indoor area unless officials instruct otherwise.')
        if p.key=='missile' and c.get('business_open'): actions.append('Guide customers and staff before protecting merchandise or payment processes.')
        if c.get('accessibility_needs'):
            flags.append('accessibility_support_required'); actions.append('Use the preassigned accessible route and buddy support.')
        return {'event':p.key,'title':p.title_en,'immediate_actions':actions,'do_not':list(p.do_not),'shelter_time':p.shelter_time,'emergency_numbers':list(p.emergency_numbers),'risk_flags':flags,'official_override':p.official_override}
    async def async_decide_action(self, event_type: str|int, context: Optional[dict[str,Any]]=None)->dict[str,Any]: return await asyncio.to_thread(self.decide_action,event_type,context)
    def household_plan(self, profile: HouseholdProfile)->Plan:
        if profile.people<=0: raise ValueError('people must be positive')
        actions=[f'Confirm protected space in {profile.city}: {profile.protected_space}.','Time the route from every room during day and night.','Clear the route and keep protected-space door/window usable.','Keep water, flashlight, radio, power bank, paper contacts, IDs, cash, and spare keys nearby.','Practice one calm drill and review monthly.']
        supplies=['water','flashlight','power bank','radio','first-aid kit','paper emergency contacts','copies of IDs']; records=['emergency contacts','medication list','insurance/lease contacts']; flags=[]
        if profile.children: actions.append('Add child roles, comfort items, diapers/formula where relevant, and simple routine cards.'); supplies.append('child comfort item')
        if profile.older_adults: actions.append('Place glasses, hearing aids, mobility aids, and medication near the bed.'); records.append('medication schedule')
        if profile.accessibility_needs: actions.append('Validate accessible route width and assign buddy support without depending on one person.'); flags.append('accessibility_route_check_required')
        if profile.pets: actions.append('Keep pet leash/carrier, water bowl, and waste bags near the protected space.'); supplies += ['pet leash/carrier','pet water bowl','waste bags']
        if profile.near_coast: actions.append('Add tsunami route: 1 km inland or 4th floor+ after coastal warning signs.'); flags.append('coastal_tsunami_awareness')
        if profile.medications: supplies.append('72-hour medication reserve where medically appropriate'); records.append('prescriptions and dosage schedule')
        return Plan('household',f'Household emergency plan for {profile.city}',tuple(actions),tuple(dict.fromkeys(supplies)),tuple(dict.fromkeys(records)),'monthly and after any home layout change',tuple(flags))
    async def async_household_plan(self, profile: HouseholdProfile)->Plan: return await asyncio.to_thread(self.household_plan,profile)
    def business_plan(self, profile: BusinessProfile)->Plan:
        if profile.employees<0 or profile.customers_peak<0: raise ValueError('employees and customers_peak cannot be negative')
        people=profile.employees+profile.customers_peak; flags=[]
        actions=[f'Assign a shift lead for the {profile.business_type} in {profile.city}.','Mark protected-space route and customer overflow area.','Train staff to stop service immediately during alerts.','Document closure time, canceled orders, staff hours, supplier issues, and ₪ impact.','Define reopening criteria: official permission, safe structure, utilities, staffing, sanitation, and payment systems.']
        supplies=['first-aid kit','flashlight','power bank','paper staff roster','supplier contacts','insurance details']; records=['employee roster','supplier list','insurance policy','lease/landlord contact','invoices','receipts','inventory','payroll records','incident log with ₪ amounts']
        if profile.protected_space_capacity is not None and profile.protected_space_capacity<people: flags.append('capacity_exceeded'); actions.append('Create overflow safe-area procedure because peak people exceed protected-space capacity.')
        if profile.stores_chemicals: flags.append('hazmat_controls_required'); actions.append('Maintain chemical inventory/safety sheets and train staff not to clean unknown spills.'); supplies.append('sealable bags/tape for official hazmat instructions')
        if profile.uses_gas: flags.append('gas_shutdown_review_required'); actions.append('Document safe gas shutoff and call 102 for gas smell after earthquakes or impacts.')
        if profile.keeps_customer_property: flags.append('customer_property_chain_of_custody'); records.append('customer property custody log')
        if profile.accessibility_needs: flags.append('accessibility_support_required'); actions.append('Assign accessible escort roles and keep route clear for mobility devices.')
        if profile.daily_revenue_nis is not None: records.append(f'daily revenue baseline: ₪{profile.daily_revenue_nis}')
        return Plan('business',f'Business continuity plan for {profile.business_type} in {profile.city}',tuple(actions),tuple(dict.fromkeys(supplies)),tuple(dict.fromkeys(records)),'monthly, after staff/layout changes, and after each incident',tuple(flags))
    async def async_business_plan(self, profile: BusinessProfile)->Plan: return await asyncio.to_thread(self.business_plan,profile)
    def go_bag(self, *, pets: bool=False, business: bool=False, medications: bool=False)->list[str]:
        items=['water','flashlight','spare batteries','power bank','radio','first-aid kit','paper emergency contacts','copy of IDs','cash','spare keys']
        if pets: items += ['pet leash/carrier','pet food','waste bags']
        if business: items += ['supplier contacts','insurance policy number','incident log sheet','receipt/invoice backup access']
        if medications: items += ['medications','prescription copy','glasses/hearing-aid batteries']
        return list(dict.fromkeys(items))
    def export_json(self, data: Protocol|Plan|dict[str,Any], path: str|Path)->Path:
        target=Path(path); payload=data.to_dict() if isinstance(data,(Protocol,Plan)) else data
        target.parent.mkdir(parents=True, exist_ok=True); target.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8'); return target


def validate_environment(value: Optional[str] = None) -> str:
    env = (value or os.getenv('DPG_ENV') or 'sandbox').strip().casefold()
    if env not in {'sandbox', 'production'}:
        raise ValueError("environment must be 'sandbox' or 'production'")
    return env


def make_plan_id(plan_type: str, city: str, environment: str = 'sandbox') -> str:
    digest = hashlib.sha256(f'{plan_type}:{city}:{environment}'.encode('utf-8')).hexdigest()[:10]
    return f'{plan_type}-{environment}-{digest}'


class PreparednessClient(_BasePreparednessClient):
    def __init__(self, protocols: Optional[dict[HazardKey, Protocol]] = None, environment: Optional[str] = None) -> None:
        super().__init__(protocols=protocols)
        self.environment = validate_environment(environment)

    def decide_action(self, event_type: str | int, context: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        payload = super().decide_action(event_type, context)
        payload['environment'] = self.environment
        return payload

    def household_plan(self, profile: HouseholdProfile, *, plan_id: Optional[str] = None) -> Plan:
        plan = super().household_plan(profile)
        return replace(
            plan,
            plan_id=plan_id or make_plan_id('household', profile.city, self.environment),
            environment=self.environment,
            created_at='2026-06-04T00:00:00Z',
        )

    def business_plan(self, profile: BusinessProfile, *, plan_id: Optional[str] = None) -> Plan:
        plan = super().business_plan(profile)
        return replace(
            plan,
            plan_id=plan_id or make_plan_id('business', profile.city, self.environment),
            environment=self.environment,
            created_at='2026-06-04T00:00:00Z',
        )

    def create_plan(self, profile: HouseholdProfile | BusinessProfile, *, plan_id: Optional[str] = None) -> dict[str, Any]:
        plan = self.household_plan(profile, plan_id=plan_id) if isinstance(profile, HouseholdProfile) else self.business_plan(profile, plan_id=plan_id)
        return {'id': plan.plan_id, 'plan': plan.to_dict(), 'environment': self.environment}

    def summarize_plan(self, plan_payload: dict[str, Any], plan_id: str) -> dict[str, Any]:
        plan = plan_payload.get('plan', plan_payload)
        actual_id = plan.get('plan_id') or plan_payload.get('id')
        if actual_id != plan_id:
            raise ValueError('plan_id does not match the provided plan payload')
        return {
            'id': plan_id,
            'title': plan.get('title'),
            'priority_action_count': len(plan.get('priority_actions', [])),
            'risk_flags': plan.get('risk_flags', []),
            'official_override': bool(plan.get('official_override', True)),
            'environment': plan.get('environment', self.environment),
        }

    def read_json(self, path: str | Path) -> dict[str, Any]:
        return json.loads(Path(path).read_text(encoding='utf-8'))

def _print_protocol(p:Protocol)->None:
    print(f'{p.title_en} / {p.title_he}'); print(p.summary); print('\nImmediate actions:')
    for a in p.immediate_actions: print(f'- {a}')
    print('\nDo not:')
    for d in p.do_not: print(f'- {d}')
    print(f'\nShelter/release: {p.shelter_time}')
    if p.emergency_numbers: print('Emergency numbers: '+', '.join(p.emergency_numbers))
    print('Official current instructions override this helper.')
async def _async_demo(q:str)->dict[str,Any]: return (await PreparednessClient().async_lookup(q)).to_dict()


def main(argv: Optional[Iterable[str]]=None)->int:
    ap=argparse.ArgumentParser(description='Offline disaster-preparedness lookup helper.')
    ap.add_argument('query')
    ap.add_argument('--json', action='store_true')
    ap.add_argument('--env', choices=['sandbox','production'], default=os.getenv('DPG_ENV','sandbox'))
    ap.add_argument('--async-demo', action='store_true')
    args=ap.parse_args(list(argv) if argv is not None else None)
    client=PreparednessClient(environment=args.env)
    try:
        if args.async_demo:
            payload=asyncio.run(_async_demo(args.query)); payload['environment']=client.environment
            print(json.dumps(payload, ensure_ascii=False, indent=2)); return 0
        p=client.lookup(args.query)
    except UnknownHazardError as e:
        print(json.dumps({'error':'UNKNOWN_EVENT_TYPE','message':str(e)}, ensure_ascii=False, indent=2)); return 2
    if args.json:
        payload=p.to_dict(); payload['environment']=client.environment
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        _print_protocol(p)
    return 0
