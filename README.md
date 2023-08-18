# CLUSTER TO CLUSTER SYNC

__Ability to achieve stressed exits from 1 cluster to another as part of multi-cluster DR strategy__

__SA Maintainer__: [Eugene Tan](mailto:eugene.tan@mongodb.com) <br/>
__Time to setup__: 10 mins <br/>
__Time to execute__: 15 mins <br/>

---
## Description

This proof shows how you can achieve a stressed exit from one MongoDB cluster to another by achieving an active-passive multi cluster DR strategy.

For this proof, an Atlas cluster will be loaded with [sample data](https://docs.atlas.mongodb.com/sample-data/). The **accounts** and **transactions** collection in the **sample_analytics** database will be written to by the application to simulate a live replication of data from the source to target cluster. This proof shows that data can be migrated and kept in realtime sync between source and target Atlas clusters as part of the cluster to cluster sync as part of a DR strategy. This proof also showcases you can also run a filtered sync to only sync a subset of collections ( **transactions** ) to the target cluster.

---
## Setup
__1. Configure Atlas Environment__
* __Note__: If using the Shared Demo Environment (https://docs.google.com/document/d/1cWyqMbJ_cQP3j7S4FJQhjRRiKq9WPfwPG6BmJL2bMvY/edit), please refer to the pre-existing collections for this PoV. (RICH-QUERY.customers & RICH-QUERY.customersIndexed)
* Log-on to your [Atlas account](http://cloud.mongodb.com) (using the MongoDB SA preallocated Atlas credits system) and navigate to your SA project
* In the project's Security tab, choose to add a new user, configure database user “ADMIN” with role “Atlas Admin”
* In the Security tab, add a new __IP Whitelist__ for your laptop's current IP address
* Create an __M10__ based 3 node replica-set in __AWS__, running on version 6.0 and name it __DEMO-AWS__ in __SYD__ region
* Create an __M10__ based 3 node replica-set in __GCP__, running on version 6.0 and name it __DEMO-GCP__ in __MELBOURNE__ region
* In the Atlas console, for the database cluster you deployed, click the __Connect button__, select __Connect Your Application__, and for the __latest Node.js version__ copy the __Connection String Only__ - make a note of this MongoDB URL address to be used in the next step for both clusters created

__2. Load Data Into A Collection In The Atlas Cluster__
* Load sample data set with the Atlas UI and verify that the data is loaded in the Atlas Data Explorer

__3. Install mongosync via the [Download Center](https://www.mongodb.com/docs/cluster-to-cluster-sync/current/installation/) and choose the correct OS your local machine runs on

__4. Once mongosync is installed, run mongosync with this command:
```bash
mongosync \
  --cluster0 'mongodb+srv://ADMIN:<password>@<demo-aws cluster connection string>/' \
  --cluster1 'mongodb+srv://ADMIN:<password>@<demo-gcp cluster connection string>/'
```
__5. Ensure mongosync is running at localhost:27182. It should have a message like so: 
```bash
{"level": "info", ... , "message": "running webserver"}
```

---
## Execution

__1. Run The Test Query to ascertain a record exists in source cluster__
* In the Atlas UI __Data Explorer__ tab, enter the following query filter on both the accounts and transactions collections in the sample_analytics database:
  ```
  FILTER: {account_id: 371138} 
  ```
* Clicking the __FIND__ button returns the matching documents:
  ![query1](img/query1.png)
* Note the number of documents returned - 63 in this example. It's also important to highlight that the client application was not involved in processing the query - all the data was found and returned by the database engine.
* Switch to the __Explain
Plan__ tab and click the __Explain__ button.
![plan1](img/plan1.png)
* Note that this query performed a 'collection scan' (__COLLSCAN__) across all 1 million documents. In this particular example 1 million documents were examined and 63 documents were returned in 3844ms. Also note that no index was used to satisfy the query.

__2. Run The Test Query Again Returning Just The Data We Need__
* Back on the __Documents__ tab click the __OPTIONS__ button and update the projection field as follows:
  ```
  PROJECT: { '_id': 0, 'firstname': 1, 'lastname': 1, 'dob': 1 }
  ```
* Click the __FIND__ button and validate the set of returned documents only include the person's name and date of birth.
![query2](img/query2.png)
* Switch back to to the __Explain Plan__ tab and execute the __Explain Plan__ again.
![plan2](img/plan2.png)
* Note that the same number of documents are returned in approximately the same amount of time (3742ms). This time however, we see a new __PROJECTION__ stage which reduces the volume of data returned to the client, minimizing network bandwidth in the response.

__3. Create An Appropriate Index__

__NOTE:__ If running this using a pre-built Shared Demo Environment, skip this section 3 (don't try to create an index) because a separate copy of the collection (_RICH-QUERY.customersIndexed_) has been created for use in section 4.

* In the Compass __Indexes__ tab, click the __Create Index__ button and add a new compound index called __index1__ with the following elements:
  ```
  FIELD: address.state, TYPE: 1 (asc)
  FIELD: policies.policyType, TYPE: 1 (asc)
  FIELD: policies.insured_person.smoking, TYPE: 1 (asc)
  FIELD: gender, TYPE: 1 (asc)
  FIELD: dob, TYPE: 1 (asc)
  ```
 ![index](img/index3.png)
 Note: For those that want to create index via cli use `db.customers.createIndex({"address.state":1, "policies.policyType":1, "policies.insured_person.smoking":1, "gender":1, "dob":1})`
* Press the _Create_ button to apply the index (the index may take a few 10s of seconds to be created against the 1m records). This index is very efficient in that it has been defined using the most specific fields in our query listed first, with the range field at the end.

__4. Run The Test Query Leveraging The New Index__

__NOTE:__ If running this using a pre-built Shared Demo Environment, a separate copy of the collection (_RICH-QUERY.customersIndexed_) has been created for use in this section, which is already indexed, so run the below steps against this separate _customersIndexed_ collection.

* In the Compass __Documents__ tab, execute the same query again and verify the same set of documents are returned as before.
* In the Compass __Explain Plan__ tab, examine the latest plan by clicking the __EXPLAIN__ button again.
![plan4](img/plan4.png)
* Here we see an 'index scan' (`IXSCAN`) is taking place instead of the earlier 'collection scan' (`COLLSCAN`).
* We also see from the plan and the metrics that only 63 index items were examined, resulting in 63 documents being fetched before the projection took place. The net result is a more efficient query taking just 18ms in this example.

&nbsp;__NOTE__: In some situations a _Covered Query_ can be used to allow the database to return the results for the query leveraging just an index, without fetching the underlying documents. In this example though, it is not possible to use a covered query due to the fact that the query targets an array field (see [Covered Queries](https://docs.mongodb.com/manual/core/index-multikey/#covered-queries) which states: `Multikey indexes cannot cover queries over array field(s)`)

---------------------------
# POV-C2CR-MULTI-CLOUD-DR

This POV demonstrates a DR strategy between 2 multi cloud clusters on MongoDB Atlas

[Demo flow](https://docs.google.com/presentation/d/1jHxID9rO8yzQCKJvLMoTWtJx3NrUkyXvg0kiS5aXznA/edit#slide=id.g22d6cc18279_0_0)
<br/>
[Demo notes](https://docs.google.com/document/d/1xjaiw1-gWM6xMRfo8g0d8EqKA7Q0iSzOxwq5WgsT060/edit)

Command:

````mongosync \
 --cluster0 'mongodb+srv://admin:password@ambankdemoonprem.g3aer.mongodb.net/' \
 --cluster1 'mongodb+srv://admin:password@ambankdemocloud.g3aer.mongodb.net/'```
````
