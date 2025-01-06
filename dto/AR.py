# DTO 역할 클래스 - getter/setter
# default값 세팅방법?
# jsonArray
# 원본파일 생성(ex. /backup/202412/20241215.json)
# 로그파일 생성(ex. /log/202412/20241215.txt)
# 설정파일 생성(ex. /config/conf.json)
import json
# from flask import jsonify

# BusinessUnit
# TransactionSource
# TransactionType
# TransactionNumber
# TransactionDate
# AccountingDate
# BillToName
# AccountNumber
# PaymentTerms
# StructuredPaymentReference(SPR)
# 세무 증빙 유형(TaxProofType)	
# 종사업장 번호(Business Number)	
# 작성자(Writer)
# E-Mail(Email)
# MemoLine	
# Description	
# Quantity	 
# UnitPrice 	
# TaxClassification	
# Transaction Business Category		
# Revenu		
# Company	
# Business	
# RESP Center	
# Cost Center	
# Account	
# SubAccount	
# Project	
# Product	
# TBD
# registerYN

class ARs:
    def __init__(self):
        self.result = []
    
    def setResult(self, ar):
        self.result.append(ar)

    def getResult(self):
        return self.result
    
    def toJsonARs(self):
        return json.dumps(self,default=lambda o:o.__dict__,sort_keys=False,indent=4, ensure_ascii=False)
        # return json.dumps(self, default=lambda o:o.__dict__, sort_keys=False, ensure_ascii=False)
        # return jsonify(self)

class AR:
    
    # BusinessUnit
    def setBusinessUnit(self, BusinessUnit):
        self.BusinessUnit = BusinessUnit

    def getBusinessUnit(self):
        return self.BusinessUnit
    
    # TransactionSource
    def setTransactionSource(self, TransactionSource):
        self.TransactionSource = TransactionSource

    def getTransactionSource(self):
        return self.TransactionSource

    # TransactionType
    def setTransactionType(self, TransactionType):
        self.TransactionType = TransactionType

    def getTransactionType(self):
        return self.TransactionType

    # TransactionNumber
    def setTransactionNumber(self, TransactionNumber):
        self.TransactionNumber = TransactionNumber

    def getTransactionNumber(self):
        return self.TransactionNumber

    # TransactionDate
    def setTransactionDate(self, TransactionDate):
        self.TransactionDate = TransactionDate

    def getTransactionDate(self):
        return self.TransactionDate

    # AccountingDate
    def setAccountingDate(self, AccountingDate):
        self.AccountingDate = AccountingDate

    def getAccountingDate(self):
        return self.AccountingDate

    # BillToName
    def setBillToName(self, BillToName):
        self.BillToName = BillToName

    def getBillToName(self):
        return self.BillToName

    # AccountNumber
    def setAccountNumber(self, AccountNumber):
        self.AccountNumber = AccountNumber

    def getAccountNumber(self):
        return self.AccountNumber

    # PaymentTerms
    def setPaymentTerms(self, PaymentTerms):
        self.PaymentTerms = PaymentTerms

    def getPaymentTerms(self):
        return self.PaymentTerms

    # StructuredPaymentReference(SPR)
    def setStructuredPaymentReference(self, StructuredPaymentReference):
        self.StructuredPaymentReference = StructuredPaymentReference

    def getStructuredPaymentReference(self):
        return self.StructuredPaymentReference

    # 세무 증빙 유형(TaxProofType)	
    def setTaxProofType(self, TaxProofType):
        self.TaxProofType = TaxProofType

    def getTaxProofType(self):
        return self.TaxProofType

    # 종사업장 번호(BusinessNumber)	
    def setBusinessNumber(self, BusinessNumber):
        self.BusinessNumber = BusinessNumber

    def getBusinessNumber(self):
        return self.BusinessNumber
    
    # 역발행여부(ReverseIssue)	
    def setReverseIssue(self, ReverseIssue):
        self.ReverseIssue = ReverseIssue

    def getReverseIssue(self):
        return self.ReverseIssue

    # 작성자(Writer)
    def setWriter(self, Writer):
        self.Writer = Writer

    def getWriter(self):
        return self.Writer

    # E-Mail(Email)
    def setEmail(self, Email):
        self.Email = Email

    def getEmail(self):
        return self.Email
    
    # RegisterYN
    def setRegisterYN(self, RegisterYN):
        self.RegisterYN = RegisterYN

    def getRegisterYN(self):
        return self.RegisterYN

    # # MemoLine	
    # def setMemoLine(self, MemoLine):
    #     self.MemoLine = MemoLine

    # def getMemoLine(self):
    #     return self.MemoLine

    # # Description	
    # def setDescription(self, Description):
    #     self.Description = Description

    # def getDescription(self):
    #     return self.Description

    # # Quantity	 
    # def setQuantity(self, Quantity):
    #     self.Quantity = Quantity

    # def getQuantity(self):
    #     return self.Quantity

    # # UnitPrice 	
    # def setUnitPrice(self, UnitPrice):
    #     self.UnitPrice = UnitPrice

    # def getUnitPrice(self):
    #     return self.UnitPrice

    # # TaxClassification	
    # def setTaxClassification(self, TaxClassification):
    #     self.TaxClassification = TaxClassification

    # def getTaxClassification(self):
    #     return self.TaxClassification

    # # Transaction Business Category(TBC)
    # def setTBC(self, TBC):
    #     self.TBC = TBC

    # def getTBC(self):
    #     return self.TBC

    # # Revenu		
    # def setRevenu(self, Revenu):
    #     self.Revenu = Revenu

    # def getRevenu(self):
    #     return self.Revenu

    # # Company	
    # def setCompany(self, Company):
    #     self.Company = Company

    # def getCompany(self):
    #     return self.Company

    # # # Business	
    # # def setBusinessUnit(self, businessUnit):
    # #     self.businessUnit = businessUnit

    # # def getBusinessUnit(self):
    # #     return self.businessUnit

    # # RESPCenter 
    # def setRESPCenter(self, RESPCenter):
    #     self.RESPCenter = RESPCenter

    # def getRESPCenter(self):
    #     return self.RESPCenter

    # # CostCenter
    # def setCostCenter(self, CostCenter):
    #     self.CostCenter = CostCenter

    # def getCostCenter(self):
    #     return self.CostCenter

    # # Account	
    # def setAccount(self, Account):
    #     self.Account = Account

    # def getAccount(self):
    #     return self.Account

    # # SubAccount	
    # def setSubAccount(self, SubAccount):
    #     self.SubAccount = SubAccount

    # def getSubAccount(self):
    #     return self.SubAccount

    # # Project	
    # def setProject(self, Project):
    #     self.Project = Project

    # def getProject(self):
    #     return self.Project

    # # Product	
    # def setProduct(self, Product):
    #     self.Product = Product

    # def getProduct(self):
    #     return self.Product

    # # TBD
    # def setTBD(self, TBD):
    #     self.TBD = TBD

    # def getTBD(self):
    #     return self.TBD
    
    # InvoiceDetails
    def setInvoiceDetails(self, InvoiceDetails):
        self.InvoiceDetails = InvoiceDetails

    def getInvoiceDetails(self):
        return self.InvoiceDetails
    
    def toJsonAR(self):
        return json.dumps(self,default=lambda o:o.__dict__,sort_keys=False,indent=4, ensure_ascii=False)


class InvoiceDetails:

    # MemoLine	
    def setMemoLine(self, MemoLine):
        self.MemoLine = MemoLine

    def getMemoLine(self):
        return self.MemoLine

    # Description	
    def setDescription(self, Description):
        self.Description = Description

    def getDescription(self):
        print(self.Description)
        return self.Description

    # Quantity	 
    def setQuantity(self, Quantity):
        self.Quantity = Quantity

    def getQuantity(self):
        return self.Quantity

    # UnitPrice 	
    def setUnitPrice(self, UnitPrice):
        self.UnitPrice = UnitPrice

    def getUnitPrice(self):
        return self.UnitPrice

    # TaxClassification	
    def setTaxClassification(self, TaxClassification):
        self.TaxClassification = TaxClassification

    def getTaxClassification(self):
        return self.TaxClassification

    # Transaction Business Category(TBC)
    def setTBC(self, TBC):
        self.TBC = TBC

    def getTBC(self):
        return self.TBC

    # Revenu		
    def setRevenu(self, Revenu):
        self.Revenu = Revenu

    def getRevenu(self):
        return self.Revenu

    # Company	
    def setCompany(self, Company):
        self.Company = Company

    def getCompany(self):
        return self.Company

    # # Business	
    def setBusinessUnit(self, businessUnit):
        self.businessUnit = businessUnit

    def getBusinessUnit(self):
        return self.businessUnit

    # RESPCenter 
    def setRESPCenter(self, RESPCenter):
        self.RESPCenter = RESPCenter

    def getRESPCenter(self):
        return self.RESPCenter

    # CostCenter
    def setCostCenter(self, CostCenter):
        self.CostCenter = CostCenter

    def getCostCenter(self):
        return self.CostCenter

    # Account	
    def setAccount(self, Account):
        self.Account = Account

    def getAccount(self):
        return self.Account

    # SubAccount	
    def setSubAccount(self, SubAccount):
        self.SubAccount = SubAccount

    def getSubAccount(self):
        return self.SubAccount

    # Project	
    def setProject(self, Project):
        self.Project = Project

    def getProject(self):
        return self.Project

    # Product	
    def setProduct(self, Product):
        self.Product = Product

    def getProduct(self):
        return self.Product

    # TBD
    def setTBD(self, TBD):
        self.TBD = TBD

    def getTBD(self):
        return self.TBD

    
    def toJsonAR(self):
        return json.dumps(self,default=lambda o:o.__dict__,sort_keys=False,indent=4, ensure_ascii=False)
    
