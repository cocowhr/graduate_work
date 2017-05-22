# coding=utf-8
__author__ = 'coco'
from django.views.decorators.csrf import csrf_exempt
from algorithm import genefunc
from algorithm import execute
from algorithm import apriorifunc
from algorithm import hmm
import pymysql
from django.shortcuts import render
from django.http import JsonResponse
import random
import os
import time


def getConnection():
    conn = pymysql.connect(host='localhost', db='supervision', user='root', passwd='root', port=3306, charset='utf8')
    return conn


def getalldata(type):
    conn = getConnection()
    cur = conn.cursor()
    context = {}
    context['table'] = []
    if type == 1:
        sql = "SELECT * FROM supervision.data_process_table"
    elif type >= 2:
        sql = "SELECT * FROM supervision.data_process_table where `id` != 3 and `stage` > 0"
    cur.execute(sql)
    res = cur.fetchall()
    tables = []
    ids = []
    descriptions = []
    stages = []
    for r in res:
        ids += [r[0]]
        tables += [r[1]]
        descriptions += [r[2]]
        if type == 1:
            stages += [r[3]]
    for i in range(len(tables))[::-1]:
        if type == 1:
            context['table'] += [get(type, tables[i], descriptions[i], ids[i], stages[i])]
        elif type >= 2:
            context['table'] += [get(type, tables[i], descriptions[i], ids[i], None)]
    return context
    cur.close()
    conn.commit()
    conn.close()


def get(type, target, description, id, stage):
    table = {}
    data = []
    table['name'] = description
    if type == 1 or type == 2:
        target = target + "_raw"
    elif type == 3:
        target = target + "_generules"
    elif type == 4:
        target = target + "_middle"
    field = getfield(target)
    ###
    res = gettable(target, 15, type - 1)
    for r in res:
        row = {}
        row['info'] = []
        row['id'] = r[0]
        for j in range(1, len(field) - 1):
            row['info'] += [r[j]]
        row['alert'] = r[len(field) - 1]
        data += [row]
    table['data'] = data
    table['field'] = field
    table['id'] = id
    if type == 1:
        table['stage'] = stage
    return table


def getfield(target):
    conn = getConnection()
    cur = conn.cursor()
    field = []
    ###获得字段###
    sql = "select Column_name from information_schema.columns where table_schema='supervision' and table_name='%s';" % (
        target)
    cur.execute(sql)
    res = cur.fetchall()
    for f in res:
        field += [f[0]]
    cur.close()
    conn.commit()
    conn.close()
    return field


def gettable(target, limit, alert):
    conn = getConnection()
    cur = conn.cursor()
    sql = "SELECT * FROM "
    sql += target
    if alert > 0:
        sql += " where `alert` = 1"
    if limit > 0:
        sql += " limit "
        sql += str(limit)
    cur.execute(sql)
    res = cur.fetchall()
    cur.close()
    conn.commit()
    conn.close()
    return res


def gettablebyfield(target, field, selectfield, limit):
    conn = getConnection()
    cur = conn.cursor()
    sql = "SELECT "
    for f in selectfield:
        sql += "`%s`," % (f)
    sql = sql[:-1]
    sql += " FROM "
    sql += target
    sql += " where "
    for ff in field:
        if ff in selectfield:
            sql += " `%s` is not null and" % (ff)
        else:
            sql += " `%s` is null and" % (ff)
    sql = sql[:-3]
    sql += " order by `support` desc"
    if limit > 0:
        sql += " limit "
        sql += str(limit)
    cur.execute(sql)
    res = cur.fetchall()
    cur.close()
    conn.commit()
    conn.close()
    return res


def rawlist(request):
    context = getalldata(1)
    return render(request, 'html/rawlist.html', context)


def getinfomationbyid(id):
    conn = getConnection()
    cur = conn.cursor()
    sql = "SELECT `name`,`description`,`stage` FROM supervision.data_process_table where id = "
    sql += str(id)
    cur.execute(sql)
    res = cur.fetchall()
    return res
    cur.close()
    conn.commit()
    conn.close()


def showmiddlelist(request, id):
    conn = getConnection()
    cur = conn.cursor()
    context = {}
    res1 = getinfomationbyid(id)
    targetnumber = res1[0][0]
    targetcodes = res1[0][0] + "_codes"  # id不能为4 即表不能为process_info
    number = {}
    field = getfield(targetnumber)
    res = gettable(targetnumber, 30, 0)
    data = []
    for r in res:
        row = []
        for j in range(len(field)):
            row += [r[j]]
        data += [row]
    number['data'] = data
    number['field'] = field
    number['id'] = id
    number['stage'] = res1[0][2]
    number['name'] = res1[0][1] + unicode("apriori数字序列表", "utf-8")
    context['number'] = number
    if id != '4':
        codes = {}
        field = getfield(targetcodes)
        res = gettable(targetcodes, 30, 0)
        data = []
        for r in res:
            row = []
            for j in range(len(field)):
                row += [r[j]]
            data += [row]
        codes['data'] = data
        codes['field'] = field
        codes['id'] = id
        codes['name'] = res1[0][1] + unicode("编码表", "utf-8")
        context['codes'] = codes
    cur.close()
    conn.commit()
    conn.close()
    return render(request, 'html/middlelist.html', context)


def showapriorilist(request, id):
    context = {}
    res1 = getinfomationbyid(id)
    target = res1[0][0] + "_middle"
    middle = {}
    field = getfield(target)
    res = gettable(target, 30, 0)
    data = []
    for r in res:
        row = {}
        row['info'] = []
        row['id'] = r[0]
        if id != '3':
            for j in range(1, len(field) - 1):
                row['info'] += [r[j]]
            row['alert'] = r[len(field) - 1]
        else:
            for j in range(1, len(field)):
                row['info'] += [r[j]]
        data += [row]
    middle['data'] = data
    middle['field'] = field
    middle['id'] = id
    middle['name'] = res1[0][1] + unicode("apriori规律表", "utf-8")
    context['middle'] = middle
    return render(request, 'html/apriorilist.html', context)


@csrf_exempt
def apriorifilter(request):
    selectfield = request.POST.getlist('parameter[]')
    selectfield.insert(0, "id")
    selectfield += ["support", "create_time", "alert"]
    id = request.POST['id']
    context = {}
    res1 = getinfomationbyid(id)
    target = res1[0][0] + "_middle"
    middle = {}
    field = getfield(target)
    res = gettablebyfield(target, field, selectfield, 30)
    data = []
    for r in res:
        row = {}
        row['info'] = []
        row['id'] = r[0]
        for j in range(1, len(selectfield) - 1):
            row['info'] += [r[j]]
        row['alert'] = r[len(selectfield) - 1]
        data += [row]
    middle['data'] = data
    middle['field'] = selectfield
    middle['id'] = id
    context['middle'] = middle
    return JsonResponse({'success': True, 'context': context})


@csrf_exempt
def getsimultaneousprocess(request):
    begintime = request.POST['begintime']
    endtime = request.POST['endtime']
    apriorifunc.get_data_process_processinfo_rules('2017-03-03', begintime, endtime)
    context = {}
    res1 = getinfomationbyid(3)
    target = res1[0][0] + "_middle"
    middle = {}
    field = getfield(target)
    res = gettable(target, -1, 0)
    data = []
    for r in res:
        row = []
        for j in range(len(field)):
            row += [r[j]]
        data += [row]
    middle['data'] = data
    middle['field'] = field
    context['middle'] = middle
    return JsonResponse({'success': True, 'context': context})


def showresultlist(request):
    conn = getConnection()
    cur = conn.cursor()
    context = {}
    res1 = getinfomationbyid(3)
    target = res1[0][0] + "_result"
    all = {}
    typeone = {}
    field = getfield(target)[:-1]  # 去除type
    sql = "SELECT * FROM "
    sql += target
    sql += " where `type`= 1"
    cur.execute(sql)
    res = cur.fetchall()
    data = []
    for r in res:
        row = []
        for j in range(len(field)):
            row += [r[j]]
        data += [row]
    typeone['data'] = data
    all['field'] = field
    context['all'] = all
    context['typeone'] = typeone
    typetwo = {}
    sql = "SELECT * FROM "
    sql += target
    sql += " where `type`= 2"
    cur.execute(sql)
    res = cur.fetchall()
    data = []
    for r in res:
        row = []
        for j in range(len(field)):
            row += [r[j]]
        data += [row]
    typetwo['data'] = data
    context['typetwo'] = typetwo
    cur.close()
    conn.commit()
    conn.close()
    return render(request, 'html/resultlist.html', context)


def getgenelist(id):
    context = {}
    res1 = getinfomationbyid(id)
    target = res1[0][0] + "_generules"
    gene = {}
    field = getfield(target)
    conn = getConnection()
    cur = conn.cursor()
    sql = "SELECT * FROM "
    sql += target
    sql += " where `fit`>0 limit 30"
    cur.execute(sql)
    res = cur.fetchall()
    cur.close()
    conn.commit()
    conn.close()
    data = []
    for r in res:
        row = {}
        row['info'] = []
        row['id'] = r[0]
        for j in range(1, len(field) - 1):
            row['info'] += [r[j]]
        row['alert'] = r[len(field) - 1]
        data += [row]
    gene['data'] = data
    gene['stage'] = res1[0][2]
    gene['field'] = field
    gene['id'] = id
    gene['name'] = res1[0][1] + unicode("遗传算法规律表", "utf-8")
    context['gene'] = gene
    return context


def showgenelist(request, id):
    context = getgenelist(id)
    return render(request, 'html/genelist.html', context)


@csrf_exempt
def genecalculate(request):
    try:
        conn = getConnection()
        cur = conn.cursor()
        parameter = request.POST.getlist('parameter[]')
        id = request.POST['id']
        context = {}
        res1 = getinfomationbyid(id)
        targetcodes = res1[0][0] + "_codes"
        seq = []
        for i in range(len(parameter)):
            sql = "SELECT id FROM "
            sql += targetcodes
            sql += " where `name`='%s' and `column`='%d'" % (parameter[i], i)
            cur.execute(sql)
            res = cur.fetchall()
            seq += [res[0][0]]
        fit = genefunc.search_fit(res1[0][0], seq)
        context['fit'] = fit
        cur.close()
        conn.commit()
        conn.close()
        return JsonResponse({'success': True, 'context': context})
    except:
        return JsonResponse({'fail': True})


@csrf_exempt
def savegene(request):
    try:
        conn = getConnection()
        cur = conn.cursor()
        parameter = request.POST.getlist('parameter[]')
        id = request.POST['id']
        res1 = getinfomationbyid(id)
        targetcodes = res1[0][0] + "_codes"
        target = res1[0][0] + "_generules"
        seq = []
        for i in range(len(parameter)):
            sql = "SELECT id FROM "
            sql += targetcodes
            sql += " where `name`='%s' and `column`='%d'" % (parameter[i], i)
            cur.execute(sql)
            res = cur.fetchall()
            seq += [res[0][0]]
        fit = genefunc.search_fit(res1[0][0], seq)
        field = getfield(target)[1:-3]  # 去掉id,alert,create_time,fit
        sql = "INSERT IGNORE INTO " + target + "("
        for i in range(len(field)):
            sql += "`" + field[i] + "`,"
        sql += "`fit`) VALUES("
        for i in range(len(field)):
            sql += "'%s'," % (parameter[i])
        sql += '%lf)' % (fit)
        cur.execute(sql)
        cur.close()
        conn.commit()
        conn.close()
        context = getgenelist(id)
        return JsonResponse({'success': True, 'context': context})
    except:
        return JsonResponse({'fail': True})


def uploadsql(request):
    start = time.clock()
    file_obj = request.FILES.get('sqlfile', None)
    tablename = request.POST['tablename']
    conn = getConnection()
    cur = conn.cursor()
    sql = "SELECT * FROM data_process_table where `name`='%s'" % (tablename)
    cur.execute(sql)
    res = cur.fetchall()
    if len(res) == 0:
        tabledescription = request.POST['tabledescription']
        sql = "Insert into data_process_table(`name`,`description`) VALUES('%s','%s') " % (tablename, tabledescription)
        cur.execute(sql)
        cur.close()
        conn.commit()
        conn.close()
        file_name = 'temp_file-%d.sql' % random.randint(0, 100000)  # 不能使用文件名称，因为存在中文，会引起内部错误
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_full_path = os.path.join(BASE_DIR, 'sqlfile')
        if not os.path.exists(file_full_path):
            os.makedirs(file_full_path)
        file_full_path = os.path.join(file_full_path, file_name)
        dest = open(file_full_path, 'wb+')
        dest.write(file_obj.read())
        dest.close()
        cmd = "mysql -u root -proot supervision < " + file_full_path
        os.system(cmd)
        os.remove(file_full_path)
        end = time.clock()
        print str(end - start) + "s"
        context = getalldata(1)
        return render(request, 'html/rawlist.html', context)
    else:
        cur.close()
        conn.commit()
        conn.close()
        return render(request, 'html/error.html')


def deletelist(request, id):
    conn = getConnection()
    cur = conn.cursor()
    sql = "SELECT name FROM data_process_table where `id`='%s'" % (id)
    cur.execute(sql)
    res = cur.fetchall()
    tablename = res[0][0]
    sql = " delete  FROM data_process_table where `id`='%s'" % (id)
    cur.execute(sql)
    sql = "DROP TABLE IF EXISTS `%s`" % (tablename)
    cur.execute(sql)
    sql = "DROP TABLE IF EXISTS `%s_raw`" % (tablename)
    cur.execute(sql)
    sql = "DROP TABLE IF EXISTS `%s_codes`" % (tablename)
    cur.execute(sql)
    sql = "DROP TABLE IF EXISTS `%s_generules`" % (tablename)
    cur.execute(sql)
    sql = "DROP TABLE IF EXISTS `%s_middle`" % (tablename)
    cur.execute(sql)
    sql = "DROP TABLE IF EXISTS `%s_result`" % (tablename)
    cur.execute(sql)
    sql = "DROP VIEW IF EXISTS `%s_count`" % (tablename)
    cur.execute(sql)
    sql = "DROP TABLE IF EXISTS `%s_except`" % (tablename)
    cur.execute(sql)
    cur.close()
    conn.commit()
    conn.close()
    context = getalldata(1)
    return render(request, 'html/rawlist.html', context)


@csrf_exempt
def getmiddlelist(request):
    start = time.clock()
    id = request.POST['id']
    conn = getConnection()
    cur = conn.cursor()
    sql = "SELECT name FROM data_process_table where `id`='%s'" % (id)
    cur.execute(sql)
    res = cur.fetchall()
    target = res[0][0]
    targetraw = target + "_raw"
    field = getfield(targetraw)[1:]  # 去掉id
    field = field[:-1]  # 去掉alert
    execute.createtable(target, field)
    execute.preexecute(target, field)
    sql = "Update data_process_table set stage='1' where `id`='%s'" % (id)
    cur.execute(sql)
    end = time.clock()
    print str(end - start) + "s"
    cur.close()
    conn.commit()
    conn.close()
    return JsonResponse({'success': True})


@csrf_exempt
def getapriorilist(request):
    start=time.clock()
    id = request.POST['id']
    conn = getConnection()
    cur = conn.cursor()
    sql = "SELECT `name`,`stage` FROM data_process_table where `id`='%s'" % (id)
    cur.execute(sql)
    res = cur.fetchall()
    target = res[0][0]
    stage = int(res[0][1]) + 2
    targetraw = target + "_raw"
    field = getfield(targetraw)[1:]  # 去掉id
    field = field[:-1]  # 去掉alert
    apriorifunc.get_table_rules(target, field)
    sql = "Update data_process_table set stage='%d' where `id`='%s'" % (stage, id)
    cur.execute(sql)
    end = time.clock()
    print str(end - start) + "s"
    cur.close()
    conn.commit()
    conn.close()
    return JsonResponse({'success': True})


@csrf_exempt
def calculategenelist(request):
    start=time.clock()
    id = request.POST['id']
    conn = getConnection()
    cur = conn.cursor()
    sql = "SELECT `name`,`stage` FROM data_process_table where `id`='%s'" % (id)
    cur.execute(sql)
    res = cur.fetchall()
    target = res[0][0]
    targetraw = target + "_raw"
    field = getfield(targetraw)[1:]  # 去掉id
    field = field[:-1]  # 去掉alert
    for i in range(0,10):
        genefunc.getrules(target, field)
    cur.close()
    conn.commit()
    conn.close()
    context = getgenelist(id)
    end = time.clock()
    print str(end - start) + "s"
    return JsonResponse({'success': True, 'context': context})


def showabnormallist(request):
    context = getalldata(2)
    return render(request, 'html/abnormallist.html', context)


def mark(request, isabnormal):  # isnormal:0标记为normal 1标记为abnormal
    tableid = request.POST['tableid']
    id = request.POST['id']
    type = request.POST['type']
    conn = getConnection()
    cur = conn.cursor()
    sql = "SELECT `name` FROM data_process_table where `id`='%s'" % (tableid)
    cur.execute(sql)
    res = cur.fetchall()
    target = res[0][0]
    if type == '1':
        targetraw = target + "_raw"
        sql = "Update %s set `alert`='%d' where `id`='%s'" % (targetraw, isabnormal, id)
        cur.execute(sql)
    elif type >= '2':
        targetraw = target + "_raw"
        targettable = ""
        if type == '2':
            targettable = target + "_generules"
        elif type == '3':
            targettable = target + "_middle"
        sql = "Update %s set `alert`='%d' where `id`='%s'" % (targettable, isabnormal, id)
        cur.execute(sql)
        sql = "select * from %s where `id`='%s'" % (targettable, id)
        cur.execute(sql)
        res = cur.fetchall()
        row = res[0][1:-3]
        field = getfield(targetraw)[1:-1]
        sql = "select id from %s where " % (targetraw)
        for i in range(len(field)):
            if field[i] == "time":
                if row[i] == unicode("凌晨", "utf-8"):
                    sql += "Hour(time) < 6 and"
                elif row[i] == unicode("上午", "utf-8"):
                    sql += "Hour(time) < 12 and"
                elif row[i] == unicode("下午", "utf-8"):
                    sql += "Hour(time) < 18 and"
                elif row[i] == unicode("晚上", "utf-8"):
                    sql += "Hour(time) < 24 and"
            else:
                if row[i]:
                    sql += " `%s` = '%s' and" % (field[i], row[i])
        sql = sql[:-3]
        cur.execute(sql)
        ids = cur.fetchall()
        for mid in ids:
            sql = "Update %s set `alert`='%d' where `id`='%s'" % (targetraw, isabnormal, mid[0])
            cur.execute(sql)
    cur.close()
    conn.commit()
    conn.close()


@csrf_exempt
def markabnormal(request):
    mark(request, 1)
    return JsonResponse({'success': True})


@csrf_exempt
def marknormal(request):
    mark(request, 0)
    return JsonResponse({'success': True})


def showgeneabnormallist(request):
    context = getalldata(3)
    return render(request, 'html/geneabnormallist.html', context)


def showaprioriabnormallist(request):
    context = getalldata(4)
    return render(request, 'html/aprioriabnormallist.html', context)


@csrf_exempt
def aprioriexceptfilter(request):
    selectids = request.POST.getlist('parameter[]')
    id = request.POST['id']
    res1 = getinfomationbyid(id)
    targetraw = res1[0][0] + "_raw"
    targetmiddle = res1[0][0] + "_middle"
    targetexcept = res1[0][0] + "_except"
    field = getfield(targetraw)
    conn = getConnection()
    cur = conn.cursor()
    sql = "TRUNCATE TABLE `%s`" % (targetexcept)
    cur.execute(sql)
    table = list(gettable(targetraw, -1, 0))
    for selectid in selectids:
        sql = "SELECT * FROM "
        sql += targetmiddle
        sql += " where `id` = '%s'" % (selectid)
        cur.execute(sql)
        res = cur.fetchall()
        filters = res[0]
        for t in table[::-1]:
            hit = True
            a = t
            for i in range(1, len(field) - 2):
                if filters[i]:
                    if field[i] == "time":
                        if filters[i] == unicode("凌晨", "utf-8"):  # 0-5:59:59
                            if t[i].hour >= 6:
                                hit = False
                        elif filters[i] == unicode("上午", "utf-8"):  # 6-11:59:59
                            if t[i].hour >= 12 or t[i].hour < 6:
                                hit = False
                        elif filters[i] == unicode("下午", "utf-8"):  # 12-17:59:59
                            if t[i].hour >= 18 or t[i].hour < 12:
                                hit = False
                        elif filters[i] == unicode("晚上", "utf-8"):  # 18-23:59:59
                            if t[i].hour < 18:
                                hit = False
                    elif filters[i] != t[i]:
                        hit = False
                        break
            if hit:
                table.remove(t)
    for t in table:
        sql = "Insert into %s (" % (targetexcept)
        sql += "`id`"
        sql += ") VALUES("
        sql += "'%s')" % (t[0])
        cur.execute(sql)
    cur.close()
    conn.commit()
    conn.close()
    return JsonResponse({'success': True})


def showexceptlist(request, id):
    table = {}
    data = []
    conn = getConnection()
    cur = conn.cursor()
    context = {}
    context['table'] = []
    sql = "SELECT * FROM supervision.data_process_table where `id` = '%s'" % (id)
    cur.execute(sql)
    res = cur.fetchall()
    targetraw = res[0][1] + "_raw"
    targetexcept = res[0][1] + "_except"
    sql = "SELECT * FROM %s " % (targetexcept)
    cur.execute(sql)
    res = cur.fetchall()
    ids = []
    for r in res:
        ids += [r[0]]
    field = getfield(targetraw)
    for m in range(0, 15):
        sql = "SELECT * FROM %s WHERE id ='%s' " % (targetraw, ids[m])
        cur.execute(sql)
        res = cur.fetchall()
        for r in res:
            row = {}
            row['info'] = []
            row['id'] = r[0]
            for j in range(1, len(field) - 1):
                row['info'] += [r[j]]
            row['alert'] = r[len(field) - 1]
            data += [row]
    table['data'] = data
    table['field'] = field
    table['id'] = id
    context['table'] = table
    return render(request, 'html/exceptlist.html', context)


def showmarkovlist(request, id):
    start = time.clock()
    table = {}
    data = []
    conn = getConnection()
    cur = conn.cursor()
    context = {}
    context['table'] = []
    sql = "SELECT * FROM supervision.data_process_table where `id` = '%s'" % (id)
    cur.execute(sql)
    res = cur.fetchall()
    target = res[0][1]
    table['name'] = res[0][2] + unicode("Markov规律表", "utf-8")
    targetraw = res[0][1] + "_raw"
    targetcodes = res[0][1] + "_codes"
    field = getfield(targetraw)
    k = 1
    for i in range(0,len(field)-1-2):
        sql = "SELECT id FROM %s where `column` = '%s'" % (targetcodes, str(i))
        cur.execute(sql)
        res = cur.fetchall()
        ids = []
        for r in res:
            ids += [r[0]]
        v = hmm.getviterbi(target, ids,len(field)-i-2)
        for v1 in v:
            row = {}
            row['info'] = []
            row['id'] = k
            k += 1
            for m in range(0,len(field)-len(v1)-2):
                row['info']+=['']
            for j in range(0, len(v1)):
                row['info'] += [v1[j]]
            data += [row]
    table['data'] = data
    table['field'] = field
    table['id'] = id
    context['hmm'] = table
    end = time.clock()
    print str(end - start) + "s"
    return render(request, 'html/markovlist.html', context)
