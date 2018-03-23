# ucs-config

## Cisco UCS Object Model Object Similarities
The Cisco UCS Object Model is a representation of all UCS objects logical or physical. The objects are all very similar, so much so that the code that makes up the UCS Python SDK (link) and the UCS PowerTool suite (link) are ninety-nine percent generated. 99% is a lot of similarities but you would never mistake a VLAN object for a Service Profile object or a Boot Policy object for a MAC Pool object. The similarity comes in the form of structure, properties, privileges, processing, etc. It is this similarity and the generated UCS Python SDK (link) code that I am going to focus on and show you how to write less code.

## Python Reflection and Dynamic Module Loading
Python (link) Reflection or Introspection (link) is a way to manage your program's current state. Whether it's an object, function, module, class, etc. Python's reflection-enabling functions like getattr(), setattr(), type(), isinstance(), callable(), etc. provide insight and control. Combine those functions with Python's dynamic module loading function import_module() and you now have the ability to write less code, much less code.

## Cisco UCS Python SDK Object Specific Code
Mostly we write code that is object-specific. For example, if you want to add a VLAN to a UCS Manager using the UCS Python SDK (link) you need to:

- Query for the FabricLanCloud so you know where to put the new VLAN
- Import the FabricVlan module
- instantiate an instance of the FabricVlan class, minimally setting these attributes
  - id
  - name
- Add the VLAN object instance to the UCS connection handle
- Commit the handle

If all went well the new VLAN is added to the Fabric Lan Cloud. The code below shows this process including the UCS handle creation code.

```Python
from ucsmsdk.ucshandle import UcsHandle
from ucsmsdk.mometa.fabric.FabricVlan import FabricVlan

handle = UcsHandle("192.168.220.201", "admin", "password")
handle.login()

fabric_lan_cloud = handle.query_dn("fabric/lan")
vlan_100 = FabricVlan(parent_mo_or_dn=fabric_lan_cloud,
                  	  name="vlan100", 
  id="100)

handle.add_mo(vlan_100)
handle.commit()

handle.logout()
```

There is nothing wrong with this code. It could be enhanced with exception handling and parameterization of username, password, UCS IP, VLAN ID, and VLAN Name. You could also add validation of those parameters as well as some command line options for the parameters. Then after you did all that you would have a Python program that adds a VLAN to UCS Manager. Considering there are thousands and thousands of UCS Manager objects you better stock up on whatever fuels your development sessions.

## Dynamically Adjusting Python Code
Python reflection enables you to write dynamically adjusting code. Code that reads object configuration from a file, perhaps for a VLAN or ANY other object or objects and then creates or updates those objects.

Regardless of the object, the Python code will not change from the original code.  The configuration file instructs the Python code which module to import, which class to instantiate and which attributes of the object to set or update.

The code in ths project is the code for a VLAN object... **actually** the is the code for **any and all** of the thousands and thousands of UCS objects. These approximately thirty lines of actual code will work for every UCS Object Model object.

## The Configuration File
The configuration file is what drives the code. The configuration file shown below has two main sections:

 - connection - indicates the connection information
 - objects - the objects to be created

```JSON
{
    "connection":
    {
        "module":"ucsmsdk.ucshandle",
        "class":"UcsHandle",
        "commit-buffer": true,
        "properties":{
            "ip":"10.10.10.10",
            "username":"admin",
            "password":"password",
            "secure":true
        }
    },
    "objects": [
        {
            "module": "ucsmsdk.mometa.fabric.FabricLanCloud",
            "class": "FabricLanCloud",
            "properties":{
                "parent_mo_or_dn": "fabric"
            },
            "message": "add vlan 700",
            "children": [
                {
                    "module": "ucsmsdk.mometa.fabric.FabricVlan",
                    "class": "FabricVlan",
                    "properties":{
                        "id": "700",
                        "name": "vlan700"
                    },
                    "message": "add vlan 700"
                },{
                    "module": "ucsmsdk.mometa.fabric.FabricVlan",
                    "class": "FabricVlan",
                    "properties":{
                        "id": "701",
                        "name": "vlan701"
                    },
                    "message": "add vlan 701"
                }
            ]
        },{
            "module": "ucsmsdk.mometa.org.OrgOrg",
            "class": "OrgOrg",
            "properties":{
                "parent_mo_or_dn": "org-root",
                "name": "prod-west"
            },
            "message": "created organization prod-west"
        },{
            "module": "ucsmsdk.mometa.org.OrgOrg",
		    "class": "OrgOrg",
		    "properties":{
                "parent_mo_or_dn": "org-root",
			    "name": "prod-east"
            },
            "message": "create organization prod-east",
		 "children": [
                {
                    "module": "ucsmsdk.mometa.org.OrgOrg",
			        "class": "OrgOrg",
			        "properties":{
				        "name": "DC01"
                    },
                    "message": "created organization prod-east/DC01"
                },{
                    "module": "ucsmsdk.mometa.org.OrgOrg",
                    "class": "OrgOrg",
                    "properties":{
                        "name": "DC02"
                    },
                    "message": "created organization prod-east/DC02"
                }
            ]
        }
    ]
}
```

JSON encoding is used in this case, but YAML or XML or anything that can be loaded into a Python dictionary will work.

The `connection` section indicates which UCS system to connect to, in the sample JSON a UCS Manager connection is specified. However, change the module "ucsmsdk.ucshandle" to "imcsdk.imchandle" and the code works with a Cisco Integrated Management Controller (CIMC) connections. The code was not changed, the configuration file was changed.

The `objects` section specifies each object to create and the object's children if the object has any children. As well, if the children objects have children those objects will be created or updated and so on until there are no more decedents.

  ## Depth-First Search is the Key
The configuration file is loaded into a Python dictionary and is traversed using a depth-first search. The image depicts a depth-first search.

[](ucsm/images/dfs.jpg)

With respect to the configuration file, in this image node 1 is the "objects" list. The second level nodes are parent level objects; node 2 is the Lan Cloud and node 5 is the root Organization. Under the Lan Cloud nodes 3 and 4 are VLANs "700" and "701". Nodes 6 and 8 are sub-organizations of the root organization; "prod-west" and "prod-east". Finally, nodes 7 and 9 are sub-organizations of the prod-east organization; "DC01" and "DC02"

Every piece of information needed to create or update a UCS Managed Object is in the configuration file; the module, the class, the parent object, the children objects and the properties for each of those objects.

The children objects only vary from the initial parent object in that their parent object is not encoded in the configuration file but inherited from the enclosing parent object.

As you can see from the code above, with all the required module, class, and attribute information in the configuration file along with the hierarchical object structure these few lines of code can create any UCS object.

The additional plus with the configuration file driven code is that new and/or updated objects are added to the configuration file or put in their own configuration file. No new code needs to be written.
The UCS Python SDK was built to work this way, the uniformity of the object model enables these capabilities for reflection-based programming.


