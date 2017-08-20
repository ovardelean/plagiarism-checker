
function timeConverter(UNIX_timestamp, line){
  if (!UNIX_timestamp){
      return null;
  }
  var a = new Date(UNIX_timestamp * 1000);
  var months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
  var year = a.getFullYear();
  var month = months[a.getMonth()];
  var date = a.getDate();
  var hour = a.getHours();
  var min = a.getMinutes();
  var sec = a.getSeconds();
  if (line){
    var time = date + ' ' + month + ' ' + year + ' - ' + hour + ':' + min + ':' + sec ;
  }
  else{
    var time = date + ' ' + month + ' ' + year + '<br>' + hour + ':' + min + ':' + sec ;
  }
  return time;
}


function request_pdfs_info(limit, name){
    data = {
        'limit': limit,
        'name': name
    };
    var return_data = null;
    $.ajax({
        type: "GET",
        url: "/pdfsInfo" ,
        success: function ( txt ) {
                    return_data = JSON.parse(txt);
                },
        data: data,
        async: false,
        timeout: 60000
        });
    return return_data;
}

function request_delete_paper(name){
    data = {
        'name': name
    };
    var return_data = null;
    $.ajax({
        type: "GET",
        url: "/deletePaper" ,
        success: function ( txt ) {
                    return_data = JSON.parse(txt);
                },
        data: data,
        async: false,
        timeout: 60000
        });
    return return_data;
}

function put_papers_info(){
    var r = new Array(), j=-1;
    var pdfsInfo = request_pdfs_info();

    r[++j] = '<table id="pages_table" cellpadding="10"><tbody><tr><th>PDF</th><th>Pages</th><th>Size</th><th>Added</th><th>Download</th><th>Delete</th></tr>';
    for (i in pdfsInfo){
        r[++j] = '<tr><td>'+pdfsInfo[i]['pdf']+'</td>';
        r[++j] = '<td>'+pdfsInfo[i]['pages']+'</td>';
        r[++j] = '<td>'+parseInt(pdfsInfo[i]['size'] / 1024)+' KB</td>';
        r[++j] = '<td>'+timeConverter(pdfsInfo[i]['insert_time'])+'</td>';
        r[++j] = '<td><button onclick="window.location.replace(\'/downloadPdf?pdf_name='+pdfsInfo[i]['pdf']+'\',\'_blank\')">Download</button></td>';
        r[++j] = '<td><button onclick="request_delete_paper(\''+pdfsInfo[i]['pdf']+'\');put_papers_info()">Delete</button></td>';
        r[++j] = '</tr>';
    }
    r[++j] = '</tbody></table>'
    document.getElementById('papers_div').innerHTML = r.join('');
}

