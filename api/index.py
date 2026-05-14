from fastapi import FastAPI
from pydantic import BaseModel
from decimal import Decimal, ROUND_HALF_UP
import bisect
from typing import Optional

app = FastAPI(title="Brazil Salary & Invoice Calculator API")
handler = app # Alias for Vercel
application = app # Alias for some WSGI/ASGI servers

# --- VLOOKUP TABLE ---
MARKUP_TABLE = [
    (Decimal('5000'), Decimal('7000')), (Decimal('6000'), Decimal('7000')), (Decimal('7000'), Decimal('7000')), 
    (Decimal('8000'), Decimal('7000')), (Decimal('9000'), Decimal('7000')), (Decimal('10000'), Decimal('7000')), 
    (Decimal('11000'), Decimal('7000')), (Decimal('12000'), Decimal('7000')), (Decimal('13000'), Decimal('7000')), 
    (Decimal('13500'), Decimal('7018')), (Decimal('14000'), Decimal('7035')), (Decimal('14500'), Decimal('7053')), 
    (Decimal('15000'), Decimal('7070')), (Decimal('15500'), Decimal('7088')), (Decimal('16000'), Decimal('7106')), 
    (Decimal('16500'), Decimal('7123')), (Decimal('17000'), Decimal('7141')), (Decimal('17500'), Decimal('7159')), 
    (Decimal('18000'), Decimal('7177')), (Decimal('18500'), Decimal('7195')), (Decimal('19000'), Decimal('7213')), 
    (Decimal('19500'), Decimal('7231')), (Decimal('20000'), Decimal('7249')), (Decimal('21000'), Decimal('7285')), 
    (Decimal('22000'), Decimal('7321')), (Decimal('23000'), Decimal('7358')), (Decimal('24000'), Decimal('7395')), 
    (Decimal('25000'), Decimal('7432')), (Decimal('26000'), Decimal('7469')), (Decimal('27000'), Decimal('7506')), 
    (Decimal('28000'), Decimal('7544')), (Decimal('29000'), Decimal('7581')), (Decimal('30000'), Decimal('7612')), 
    (Decimal('31000'), Decimal('7642')), (Decimal('32000'), Decimal('7673')), (Decimal('33000'), Decimal('7704')), 
    (Decimal('34000'), Decimal('7734')), (Decimal('35000'), Decimal('7765')), (Decimal('36000'), Decimal('7796')), 
    (Decimal('37000'), Decimal('7828')), (Decimal('38000'), Decimal('7859')), (Decimal('39000'), Decimal('7890')), 
    (Decimal('40000'), Decimal('7922')), (Decimal('41000'), Decimal('7954')), (Decimal('42000'), Decimal('7985')), 
    (Decimal('43000'), Decimal('8017')), (Decimal('44000'), Decimal('8049')), (Decimal('45000'), Decimal('8082')), 
    (Decimal('46000'), Decimal('8114')), (Decimal('47000'), Decimal('8158')), (Decimal('48000'), Decimal('8211')), 
    (Decimal('49000'), Decimal('8265')), (Decimal('50000'), Decimal('8318')), (Decimal('51000'), Decimal('8372')), 
    (Decimal('52000'), Decimal('8427')), (Decimal('53000'), Decimal('8482')), (Decimal('54000'), Decimal('8537')), 
    (Decimal('55000'), Decimal('8592')), (Decimal('56000'), Decimal('8648')), (Decimal('57000'), Decimal('8704')), 
    (Decimal('58000'), Decimal('8761')), (Decimal('59000'), Decimal('8818')), (Decimal('60000'), Decimal('8875')), 
    (Decimal('61000'), Decimal('8933')), (Decimal('62000'), Decimal('8991')), (Decimal('63000'), Decimal('9049')), 
    (Decimal('64000'), Decimal('9108')), (Decimal('65000'), Decimal('9167')), (Decimal('66000'), Decimal('9227')), 
    (Decimal('67000'), Decimal('9287')), (Decimal('68000'), Decimal('9347')), (Decimal('69000'), Decimal('9408')), 
    (Decimal('70000'), Decimal('9469')), (Decimal('71000'), Decimal('9530')), (Decimal('72000'), Decimal('9568')), 
    (Decimal('73000'), Decimal('9606')), (Decimal('74000'), Decimal('9645')), (Decimal('75000'), Decimal('9683')), 
    (Decimal('76000'), Decimal('9722')), (Decimal('77000'), Decimal('9761')), (Decimal('78000'), Decimal('9800')), 
    (Decimal('79000'), Decimal('9839')), (Decimal('80000'), Decimal('9879')), (Decimal('81000'), Decimal('9918')), 
    (Decimal('82000'), Decimal('9958')), (Decimal('83000'), Decimal('9998')), (Decimal('84000'), Decimal('10038')), 
    (Decimal('85000'), Decimal('10078')), (Decimal('86000'), Decimal('10118')), (Decimal('87000'), Decimal('10159')), 
    (Decimal('88000'), Decimal('10199')), (Decimal('89000'), Decimal('10240')), (Decimal('90000'), Decimal('10281')), 
    (Decimal('91000'), Decimal('10322')), (Decimal('92000'), Decimal('10363')), (Decimal('93000'), Decimal('10405')), 
    (Decimal('94000'), Decimal('10446')), (Decimal('95000'), Decimal('10488')), (Decimal('96000'), Decimal('10530')), 
    (Decimal('97000'), Decimal('10572')), (Decimal('98000'), Decimal('10615')), (Decimal('99000'), Decimal('10657')), 
    (Decimal('100000'), Decimal('10700')), (Decimal('101000'), Decimal('10742')), (Decimal('102000'), Decimal('10785')), 
    (Decimal('103000'), Decimal('10829')), (Decimal('104000'), Decimal('10872')), (Decimal('105000'), Decimal('10915')), 
    (Decimal('106000'), Decimal('10959')), (Decimal('107000'), Decimal('11003')), (Decimal('108000'), Decimal('11047')), 
    (Decimal('109000'), Decimal('11091')), (Decimal('110000'), Decimal('11135')), (Decimal('111000'), Decimal('11180')), 
    (Decimal('112000'), Decimal('11225')), (Decimal('113000'), Decimal('11270')), (Decimal('114000'), Decimal('11315')), 
    (Decimal('115000'), Decimal('11360')), (Decimal('116000'), Decimal('11405')), (Decimal('117000'), Decimal('11451')), 
    (Decimal('118000'), Decimal('11497')), (Decimal('119000'), Decimal('11543')), (Decimal('120000'), Decimal('11589'))
]

MARKUP_KEYS = [row[0] for row in MARKUP_TABLE]
MARKUP_VALS = [row[1] for row in MARKUP_TABLE]

# --- INPUT MODEL ---
class SalaryInputBrazil(BaseModel):
    gross_salary: Decimal
    food_stipend: Decimal
    exchange_rate: Decimal
    custom_markup_gbp: Optional[Decimal] = None

def get_markup(total_per_annum_gbp: Decimal) -> Decimal:
    if total_per_annum_gbp < MARKUP_KEYS[0]:
        return MARKUP_VALS[0]
    idx = bisect.bisect_right(MARKUP_KEYS, total_per_annum_gbp) - 1
    if idx >= len(MARKUP_VALS):
        idx = len(MARKUP_VALS) - 1
    return MARKUP_VALS[idx]

def d_round(val: Decimal) -> Decimal:
    return val.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

# --- API ENDPOINTS ---
@app.get("/")
@app.get("/api")
def read_root():
    return {"status": "ok", "message": "Brazil Salary & Invoice Calculator API is running"}

@app.post("/api/calculate/brazil")
@app.post("/calculate/brazil")
def calculate_brazil_finance(data: SalaryInputBrazil):
    # 1. Local BRL Calculations
    health_insurance = Decimal('263') * 1 # Monthly cost
    bonus_13th = data.gross_salary * Decimal('0.0833')
    vacation_bonus = data.gross_salary * Decimal('0.0277')
    
    # Employer taxes (estimates)
    social_security = data.gross_salary * Decimal('0.20') # Employer INSS
    social_tax = data.gross_salary * Decimal('0.058')    # Other entities
    workers_accident_insurance = data.gross_salary * Decimal('0.02') # RAT
    severance_fund = data.gross_salary * Decimal('0.08') # FGTS
    
    # Cost To Company (Monthly)
    ctc_monthly = (
        data.gross_salary + 
        data.food_stipend + 
        health_insurance + 
        social_security + 
        social_tax + 
        workers_accident_insurance + 
        bonus_13th + 
        vacation_bonus + 
        severance_fund
    )
    total_per_annum_brl = ctc_monthly * 12

    # 2. Conversion & Markup (GBP Calculations)
    total_per_annum_gbp = total_per_annum_brl / data.exchange_rate
    
    if data.custom_markup_gbp and data.custom_markup_gbp > 0:
        mark_up_gbp = data.custom_markup_gbp
    else:
        mark_up_gbp = get_markup(total_per_annum_gbp)
    
    fully_loaded_resource_cost = total_per_annum_gbp + mark_up_gbp
    recruitment_fee = fully_loaded_resource_cost * Decimal('0.10')
    
    # 3. Monthly Invoice Breakdown (GBP)
    cost_per_month_gbp = fully_loaded_resource_cost / 12
    office_cost_gbp = Decimal('1400.00') / 12
    technology_cost_gbp = Decimal('850.00') / 12
    
    total_monthly_invoice_ex_vat = cost_per_month_gbp + office_cost_gbp + technology_cost_gbp
    total_cost_annual = total_monthly_invoice_ex_vat * 12
    
    return {
        "local_salary_brl": {
            "gross_salary": d_round(data.gross_salary),
            "food_stipend": d_round(data.food_stipend),
            "health_insurance": d_round(health_insurance),
            "13th_month_bonus": d_round(bonus_13th),
            "vacation_bonus": d_round(vacation_bonus),
            "social_security_employer": d_round(social_security),
            "social_tax": d_round(social_tax),
            "workers_accident_insurance_rat": d_round(workers_accident_insurance),
            "severance_fund_fgts": d_round(severance_fund),
            "ctc_monthly": d_round(ctc_monthly),
            "total_per_annum_brl": d_round(total_per_annum_brl)
        },
        "invoicing_gbp": {
            "total_per_annum_gbp": d_round(total_per_annum_gbp),
            "mark_up": d_round(mark_up_gbp),
            "fully_loaded_resource_cost": d_round(fully_loaded_resource_cost),
            "recruitment_fee_once_off": d_round(recruitment_fee),
            "cost_per_month": d_round(cost_per_month_gbp),
            "office_cost_monthly": d_round(office_cost_gbp),
            "technology_cost_monthly": d_round(technology_cost_gbp),
            "total_monthly_invoice_ex_vat": d_round(total_monthly_invoice_ex_vat),
            "total_cost_annual": d_round(total_cost_annual)
        }
    }

