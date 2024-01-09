from fastapi import FastAPI, File, UploadFile, Request
from fastapi.staticfiles import StaticFiles
from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import pandas as pd
import os
import config as cfg
pd.set_option("display.float_format", lambda x: "%.2f" % x)

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.include_router(APIRouter())
app.mount("/static", StaticFiles(directory='static'), name="static")
print(os.path.dirname(os.path.abspath(__file__)) + "/static")
df=''
@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html",{"request": request})

@app.post("/upload")
async def upload_file(request:Request, file: UploadFile = File(...)):
    content = await file.read()
    global df
    df = pd.read_excel(content)
    
    table = df.to_html(classes='customers')


    return templates.TemplateResponse("upload.html", {"request": request, "table": table})


@app.post("/process_text")
async def process_text(request: Request):
    data = await request.json()
    text = data.get("text")
    processed_text = text.lower()
    com,cmd,company='','',''
    fulltext=[]
    if processed_text.startswith('ассистент'):
        cmd = processed_text
        for x in cfg.VA_ALIAS:
            cmd = cmd.replace(x, "").strip()
        com = cfg.recognize_cmd(' '.join(cmd.split()[0:2]))
        cmd = ' '.join(cmd.split()[2:])
        company = ''
        if com=='showrows':
            numrows = df.shape[0]
            return f'В таблице {numrows} строк'
        if com=='showcols':
            numrows = df.shape[1]
            return f'В таблице {numrows} столбцов'
        elif com == 'show1' or com == 'show2':
            company = cfg.recognize_company(cmd)
            companykey = cfg.get_key_by_value(cfg.sootvetstvie, company)
            filtered_df = df[(df['Заказчик'] == companykey) & (df['Недогруз/Перегруз'] < 0)]
            for index, row in filtered_df.iterrows():
                item = cfg.convert_numbers_to_words(row['Синоним'])
                n1 = row["Недогруз/Перегруз"] * -1
                n2 = row["Склад факт"]
                n3 = row["Сум. мес. потребность"]
                n4 = row["План производства"]
                n5 = round(n2 - n1 - n3 + n4,2)
                arr = [n1, n2, n3, n4, n5]
                arr = [round(x) for x in arr]
                EI = row['ЕИ']
                ei = ''

                if EI == 'КГ':
                    ei = 'кг'
                if EI == 'ТН':
                    ei = 'тээн'
                if EI == 'М':
                    ei = 'эм'
                if EI == 'ШТ':
                    ei = 'штук'
                if EI == 'М':
                    ei = 'метр'
                s1 = f'долг за предыдущий период {str(arr[0])} {ei}'
                s2 = f'на складе {str(arr[1])} {ei}'
                s3 = f'отгрузка текущего месяца {str(arr[2])} {ei}'
                s4 = f'производственная программа {str(arr[3])} {ei}'
                if n5 < 0:
                    s5 = f'прогнозное отклонение  {str(arr[4]*-1)} {ei}'
                else:
                    s5 = f'прогнозное отклонение отсутствует'
                tempstring = item+' '+ s1+' '+s2 +' '+ s3+' '+s4 +' ' +s5+' '
                desired_length = 250
                while len(tempstring) < desired_length:
                    tempstring += " "
                fulltext.append(tempstring)
            return ''.join(fulltext)
    return 'не распознано'

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)