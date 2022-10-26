const mysql = require('mysql');
    var con = mysql.createConnection({
        host: "localhost",
        user: "root",
        password: "12345",
        database: "users"
      });
      
      con.connect(function(err) {
        if (err) throw      con.end();;
        console.log("Connected!");
        var sql = "INSERT INTO user (firstName,lastName,username,password) VALUES ('kandil', '0','0','0')";
        con.query(sql, function (err, result) {
          if (err)       con.end();;
          console.log("1 record inserted");
          con.end();
        });
      });
