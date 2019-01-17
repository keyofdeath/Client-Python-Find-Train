#!/usr/bin/env python
# -*- coding: utf-8 -*-

from zeep import Client

client = Client('http://localhost:8080/TD1Service_war_exploded/services/HelloWorld?wsdl')
res = client.service.sayHelloWorldFrom("bob")
print(res)
