
function request_query_text(data){
    var data = {
        'query': data
    };
    var return_data = null;
    $.ajax({
        type: "GET",
        url: "/queryText" ,
        success: function ( txt ) {
                    return_data = JSON.parse(txt);
                },
        data: data,
        async: false,
        timeout: 60000
        });
    return return_data;
}

function request_checkPdf(fdata){
    var return_data = null;
    $.ajax({
        type: 'POST',
        url: '/checkPdf',
        data:fdata,
        contentType: false,
        processData: false,
        async: false,
        success: function(txt)
        {
            return_data = JSON.parse(txt);
        }
    });
    return return_data;
}

function put_loading(html_item){

    var s = '<center><img src="/static/img/loading_spinner.gif" style="width:100px;height:100px" alt="processing"></center>';
    document.getElementById(html_item).innerHTML = s;
}

function put_result_header(score, sources, phrases){
    var s = "";
    s += '<span style="font-size: 200%;font-weight: bold;">Score '+score+'%</span><br>'
    if (sources == 1){
        s += '<span>'+phrases+' phrases found in '+sources+' source</span><br>';
    }
    else{
        s += '<span>'+phrases+' phrases found in '+sources+' sources</span><br>';
    }
    document.getElementById("result_text_title").innerHTML = s;

}

function put_phrases(phrases){
    var t = '';
    document.getElementById("result_details_div").innerHTML = '';
    for (i in phrases) {
        console.log(phrases[i]);
        t = '<div><span style="background-color:pink">' + phrases[i]['content'] + '</span><br>';
        t += '<span style="margin-left:50%;font-size:90%;font-weight: bold">' + phrases[i]['paper'] + ' page ' + phrases[i]['page'] + '</span><br><br></div>';
        document.getElementById("result_details_div").innerHTML += t;
    }
}

function put_pdf_result_header(pdf_name, score, sources, paragraphs){
    var s = "";
    s += '<span>Pdf: '+pdf_name+'</span><br>'
    s += '<span style="font-size: 200%;font-weight: bold;">Score '+score+'%</span><br>'
    if (sources == 1){
        s += '<span>'+paragraphs+' paragraphs found in '+sources+' source</span><br>';
    }
    else{
        s += '<span>'+paragraphs+' paragraphs found in '+sources+' sources</span><br>';
    }
    document.getElementById("result_text_title").innerHTML = s;
}

function put_pdf_tops(top_hits, result_file){
    var t = '';
    document.getElementById("result_details_div").innerHTML = '';
    t = '<span style="margin-left:20%;font-weight:bold"> Top sources:</span><br><br>';
    console.log(top_hits);
    for (i in top_hits) {
        t += '<span style="margin-left:30%;font-size:20px"><b>' + top_hits[i][0] + '</b>: paragraphs ' + top_hits[i][1]['hits'] + ' from ' + top_hits[i][1]['hits'] + ' pages' + '</span><br><br>';
    }
    t += '<br><center><button onclick="window.location.replace(\'/downloadResult?result_file='+result_file+'\',\'_blank\')">Download Full Result</button></center>'
    document.getElementById("result_details_div").innerHTML = t;

}

function put_search_result(){
    var textData = document.getElementById("search_textarea").value;
    var solution = request_query_text(textData);
    console.log(solution);
    document.getElementById("result_div").style.display = 'inline-block';
    put_result_header(solution.score, solution.sources, solution.phrases);
    put_phrases(solution.phrase_hits);

}

function put_pdf_result(result){
    console.log(result);
    put_pdf_result_header(result.pdf_name, result.score, result.sources, result.paragraphs);
    put_pdf_tops(result.top_results, result.result_file);
}

function checkPdf(){
    document.getElementById('result_div').style.display = 'inline-block';
    document.getElementById("result_text_title").innerHTML = '';
    put_loading("result_details_div");

    var fdata = new FormData();

    console.log($("#checkPdfInput")[0].files[0]);

    if($("#checkPdfInput")[0].files.length>0){
        fdata.append("file",$("#checkPdfInput")[0].files[0])
    }

    var res = request_checkPdf(fdata);
    put_pdf_result(res);


}
