import urllib, urllib2
from scalefunder.lib.payment.payment_receipt_manager import PaymentReceiptManager
from scalefunder.lib.payment.payment_manager import PaymentManager
from scalefunder.models.db.engine.standard.sys.org_items.payment_field_map import PaymentFieldMap 
from scalefunder.models.db.engine.standard.sys.org_items.payment_settings import PaymentSettings
from pyramid.view import view_config
import json
from scalefunder.lib.forms.formatters import error_float,error_reg,error_admin
from webhelpers.html import tags as h
from pyramid.renderers import render_to_response, render
from scalefunder.lib.api import HMACSign,HMACScaleFunder
from pyramid.response import Response
from formencode import htmlfill
import formencode
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.url import route_url
from formencode import htmlfill
from copy import deepcopy,copy
from pyramid.response import Response
from scalefunder.models.views.viewobj.display.payment_system_display import PaymentSystemDisplay
from scalefunder.models.views.viewobj.forms.org_payment_mapping_form import OrgPaymentMappingForm
from scalefunder.models.views.viewobj.forms.org_payment_settings_form import OrgPaymentSettingsForm
from scalefunder.models.views.viewobj.forms.org_form import OrgEditForm
from scalefunder.models.db.engine.standard.sys.org_items.payment_settings import PaymentSettings
from scalefunder.models.views.view_client import ViewClient
from scalefunder.lib.display.admin.admin_nav_manager import ProjectAdminNav, ProjectAdminNew, UserAdminNav,OrgAdminNav,OrgAdminStyleNav,ProjectAdminMediaNav, TopAdminNav,ProjectStateOverviewNav,OrgPaymentNav, OrgPaymentEmpty,ProjectCreatorAdminNav, RootAdminNav, PagesAdminNav,OrgPaymentTop
from scalefunder.lib.decorators import permcheck
from scalefunder.models.db.engine.standard.sys.org import Org
#@view_config(route_name='admin_create_payment_service')
#def admin_create_payment_service(request):
    #oOrg = request.org
#    return Response(render("/admin/org/admin_org_payment_create.mako"))

@view_config(decorator=permcheck(action="edit_payment",obj_type=Org.coll()),route_name='admin_payment_active_save')
def admin_payment_active_save(request):
    sPaymentId = request.params.get("payment_system","").strip()
    if sPaymentId:
        if not sPaymentId == request.org.attr("active_payment_sys"):
            request.org.set("active_payment_sys",sPaymentId)
            request.datastore.store(request.org)
    return HTTPFound(location=request.route_url("admin_payment_service_list"))

@view_config(decorator=permcheck(action="edit_payment",obj_type=Org.coll()),route_name='admin_payment_service_list')
def admin_payment_service_list(request):
    oOrg = request.org
    lPaymentSystems = request.datastore.fetch(PaymentSettings,org_id=request.org.id).all()
    if len(lPaymentSystems) > 0:
        oTableView = ViewClient(request).table(PaymentSystemDisplay,lPaymentSystems)
    else:
        oTableView = None
    oNav = OrgPaymentTop("or","pt","pt",None,request,request.c)
    request.c.admin_nav = oNav
    oNav.initialize()
    sList = render("/admin/org/admin_org_payment_list.mako",{"oTableView":oTableView},request=request)
    dData = {'payment_system': "%s" % request.org.attr("active_payment_sys","")}
    return Response(htmlfill.render(sList,defaults=dData))

@view_config(decorator=permcheck(action="edit_payment",obj_type=Org.coll()),
route_name="admin_org_payment",renderer="admin/org/admin_org_payment.mako")
def admin_org_payment(request):

    oOrg = request.org
    oClient = request.datastore
    oSettings = None
    if request.params.get("psid"):
        oSettings = oClient.fetch(PaymentSettings,_id=request.params.get("psid"),org_id=oOrg.id).first()
    request.c.paymentform = ViewClient(request).form(OrgPaymentSettingsForm,'edit_payment_settings',{'form_label':'admin-desc-form-label'}) 
    if oSettings:
        dData = copy(oSettings.data)
        dData["psid"] = "%s" % oSettings.attr("_id")
        oNav = OrgPaymentNav("or", "pt", "ps",oSettings,request,request.c)
        oNav.initialize()
        request.c.admin_nav = oNav
        sHtml = render("admin/org/admin_org_payment.mako",{},request=request)
        return Response(htmlfill.render(
            sHtml,
            defaults=dData,
            force_defaults=False
        ))
    oNav = OrgPaymentNav("or", "pt", "ps",None,request,request.c)
    oNav.initialize()
    request.c.admin_nav = oNav
    return {}

@view_config(decorator=permcheck(action="edit_payment",obj_type=Org.coll()),
route_name="admin_org_payment_mapping",renderer="admin/org/admin_org_payment_mapping.mako")
def admin_org_payment_mapping(request):
    if not request.params.get("psid"):
        raise Exception, "No Settings"
    oOrg = request.org 
    oClient = request.datastore 
    oSettings = None
    oSettings = oClient.fetch(PaymentSettings,org_id=oOrg.id,_id=request.params.get("psid")).first()
    oProvider = oSettings.provider
    request.c.paymentform = ViewClient(request).form(OrgPaymentMappingForm,oProvider.attr("sys_code"),{'form_label':'admin-desc-form-label'}) 

    if not oSettings:
        raise Exception, "Can't have mapping without settings"
    oMapping = oClient.fetch(PaymentFieldMap,payment_settings_id=oSettings.attr("_id"),org_id=oOrg.attr("_id")).first()
    dData = dict([('psid',"%s" % oSettings.attr("_id"))])
    oNav = OrgPaymentNav("or", "pt", "pm",oSettings,request,request.c)
    oNav.initialize()
    request.c.admin_nav = oNav
    #raise Exception, oMapping
    if oMapping:
        dMap = copy(oMapping.data)
        dData = dict(dMap.items() + dData.items())
        dData["pm_id"] = "%s" % oMapping.attr("_id")
    sHtml = render("admin/org/admin_org_payment_mapping.mako",{},request=request)
    return Response(htmlfill.render(
            sHtml,
            defaults=dData,
            force_defaults=False
    ))
    return {}

@view_config(decorator=permcheck(action="edit_payment",obj_type=Org.coll()),
route_name="admin_org_payment_save")
def admin_org_payment_save(request):
    oOrg = request.org
    form_result = None
    form_errors = None
    oNav = OrgPaymentNav("or","pt","ps",None,request,request.c)
    oNav.initialize()
    request.c.admin_nav = oNav
    request.c.paymentform = ViewClient(request).form(OrgPaymentSettingsForm,'edit_payment_settings',{'form_label':'admin-desc-form-label'}) 
    schema =request.c.paymentform.schema() 
    try:
        form_result = schema.to_python(dict(request.params))
    except formencode.Invalid, error:
        form_result = error.value
        form_errors = error.error_dict or {}
        request.c.paymentform.error_set(True)
        sId = form_result.get("psid")
        if sId:
            form_result["psid"] = sId
            oNav = OrgPaymentNav("or","pt","ps",None,request,request.c)
            oNav.initialize()
            request.c.admin_nav = oNav
        sPage = render("admin/org/admin_org_payment.mako",{},request=request)
        return Response(htmlfill.render(
            sPage,
            defaults = form_result,
            errors = form_errors,
            error_class="error-input",
            auto_error_formatter=error_admin,
            prefix_error=False
            ))
    else:
        oPaymentMan = PaymentManager(request)
        oPayment = oPaymentMan.save_settings(form_result)
        if not request.org.attr("active_payment_sys"):
            request.org.set("active_payment_sys",oPayment.attr("_id"))
            request.datastore.store(request.org)
        return HTTPFound(route_url('admin_org_payment',request,_query={'s':'1','psid':"%s" % oPayment.attr("_id")}))

@view_config(decorator=permcheck(action="edit_payment",obj_type=Org.coll()),
route_name="admin_org_payment_mapping_save")
def admin_org_payment_mapping_save(request):
    oOrg = request.org
    form_result = None
    form_errors = None
    sPsid = request.params.get("psid")
    oSettings = request.datastore.fetch(PaymentSettings,org_id=oOrg.id,_id=sPsid).first()
    if not oSettings:
        raise Exception, "Can't have mapping without settings"
    request.c.paymentform = ViewClient(request).form(OrgPaymentMappingForm,oSettings.provider.attr("sys_code"),{'form_label':'admin-desc-form-label'}) 
    schema =request.c.paymentform.schema() 
    try:
        form_result = schema.to_python(dict(request.params))
    except formencode.Invalid, error:
        form_result = error.value
        form_errors = error.error_dict or {}
        request.c.paymentform.error_set(True)
        oNav = OrgPaymentNav("or","pt","pm",None,request,request.c)
        oNav.initialize()
        request.c.admin_nav = oNav
        sPage = render("admin/org/admin_org_payment_mapping.mako",{},request=request)
        return Response(htmlfill.render(
            sPage,
            defaults = form_result,
            errors = form_errors,
            error_class="error-input",
            auto_error_formatter=error_admin,
            prefix_error=False
            ))
    else:
        oPaymentMan = PaymentManager(request)
        oPayment = oPaymentMan.save_mapping(form_result)
        ##if not form_result.get("ps_id"):
         ##   return HTTPFound(route_url('project_state_overview',request,_query={'id': "%s" %  oProj.attr("_id"), 's':'1'}))
        return HTTPFound(route_url('admin_org_payment_mapping',request,_query={'psid':sPsid,'s':'1'}))

@view_config(decorator=permcheck(action="edit_payment",obj_type=Org.coll()), route_name="admin_org_payment_test")
def admin_org_payment_test(request):
    oOrg = request.org
    oNav = OrgPaymentNav("or","pt","",None,request,request.c)
    oNav.initialize()
    request.c.admin_nav = oNav
    oSettings = request.datastore.fetch(PaymentSettings,org_id=request.org.id,_id=request.org.attr("active_payment_sys")).first()
    sPingUrl = oSettings.provider.attr("ping_url")
    dRet = dict()
    dRet["sPingUrl"] = "https://{0}/{1}".format(request.org.domain(request),sPingUrl)
    return Response(render("/admin/org/payment_test_form.mako",dRet,request=request))

@view_config(decorator=permcheck(action="edit_payment",obj_type=Org.coll()), route_name="admin_org_payment_test_submit")
def admin_org_payment_test_submit(request):
    oOrg = request.org
    dParams = dict()
    oOrg = request.org
    oNav = OrgPaymentNav("or","pt","",None,request,request.c)
    oNav.initialize()
    request.c.admin_nav = oNav
    oSettings = request.datastore.fetch(PaymentSettings,org_id=request.org.id,_id=request.org.attr("active_payment_sys")).first()
    sPingUrl = oSettings.provider.attr("ping_url")
    for i in range(0,10):
        if not request.params.get("field_name_{0}".format(i),"").strip() == "":
            dParams[request.params.get("field_name_{0}".format(i))] = request.params.get("field_value_{0}".format(i))
    oHmac = HMACScaleFunder()
    sSig = oHmac.request_sig(dParams,request.org.attr("app_secret"))
    sConcat = oHmac.get_concat_string(dParams)
    dParams["sf_sig"] = sSig
    sCurlString = urllib.urlencode(dParams)
    dRender = dict()
    dRender["sConcatString"] = sConcat
    dRender["sSig"] = sSig
    dRender["sPingUrl"] = "https://{0}/{1}".format(request.org.domain(request),sPingUrl)
    dRender["sCurlString"] = sCurlString
    dRender["sPingResp"] = ""
    if dParams.get("sf_don_id") and dParams.get("sf_amount"):
        req = urllib2.Request(dRender["sPingUrl"], sCurlString)
        response = urllib2.urlopen(req)
        the_page = response.read()
        dRender["sPingResp"] = the_page
    sHtml = render("/admin/org/payment_test_form_result.mako",dRender,request=request)
    return Response(htmlfill.render(sHtml,
            defaults = request.params
    ))

@view_config(decorator=permcheck(action="edit_payment",obj_type=Org.coll()), route_name="admin_org_payment_receipt")
def admin_org_payment_receipt(request):
    oOrg = request.org
    oNav = OrgPaymentTop("or","pt","rc",None,request,request.c)
    oNav.initialize()
    request.c.admin_nav = oNav
    request.c.receiptform = ViewClient(request).form(OrgEditForm,'email_receipt_form',{'form_label':'admin-desc-form-label'}) 
    sHtml = render("/admin/org/admin_receipt.mako",{},request=request)
    dData = request.org.data
    sFilled = htmlfill.render(sHtml,defaults=dData,force_defaults=False)
    return Response(sFilled)



@view_config(decorator=permcheck(action="edit_payment",obj_type=Org.coll()), route_name="admin_org_payment_receipt_save",renderer="json")
def admin_org_payment_receipt_save(request):
    oOrg = request.org
    #oNav = OrgPaymentNav("or","pt","rc",None,request,request.c)
    #oNav.initialize()
    #request.c.admin_nav = oNav
    request.c.receiptform = ViewClient(request).form(OrgEditForm,'email_receipt_form',{'form_label':'admin-desc-form-label'}) 

    schema =request.c.receiptform.schema() 
    try:
        form_result = schema.to_python(dict(request.params))
    except formencode.Invalid, error:
        form_result = error.value
        form_errors = error.error_dict or {}
        sPage = render("admin/org/admin_receipt.mako",{},request=request)
        sHtml =  htmlfill.render(
            request.c.receiptform.render_fields(),
            defaults = form_result,
            error_formatters={'admin_error':error_admin},
            errors = form_errors,
            error_class="error-input",
            auto_error_formatter=error_admin,
            prefix_error=False
            )
        return {'status':1,'html':sHtml}
    else:
        oPaymentMan = PaymentReceiptManager(request)
        oPaymentReceipt = oPaymentMan.save_receipt(form_result)
        return {'status':0}
