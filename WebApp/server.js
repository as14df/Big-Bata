const express = require('express');
const bodyParser = require('body-parser');
const mysql = require('mysql');

const app = express()

app.use(express.static('public'));
app.use(bodyParser.urlencoded({ extended: true }));

app.set('view engine', 'ejs')

app.get('/', function (req, res) {
	res.render('index' , {result: ""});
})

app.listen(3000, function () {
  	console.log('Example app listening on port 3000!')
})

app.post('/', function (req, res) {

	var myMap = new Map();
	myMap.set("country", req.body.country);
	myMap.set("city", req.body.city);
	myMap.set("postcode", req.body.postcode);
	myMap.set("street", req.body.street);
	myMap.set("number", req.body.number);

	var sql = "select case when count(*) > 0 then 'The address is valid :)' else 'The address is invalid :(' end as result from final_address_data where '";

	for(const [key, value] of myMap.entries()){
		if( value ){
			sql += key + " like '" + value + "' and ";
		}
	}

	sql = sql.substring(0, sql.length - 5);
	sql += ";";

	console.log(sql)

	var con = mysql.createConnection({
	  host: 'mysql',
	  port: 3306,
	  user: 'root',
	  password: 'admin123',
	  database: 'db'
	});

	con.connect(function(err) {
  		if (err) throw err;
  		console.log("Connected!");

  		con.query(sql, function (err, result) {

    		if (err) throw err;
    		console.log("Result: " + result[0].result);

    		res.render('index' , {result: result[0].result});
  		});
	});
})