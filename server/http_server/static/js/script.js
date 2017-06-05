
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

function put_result_header(score, sources, phrases){
    var s = "";
    s += '<span style="font-size: 200%;font-weight: bold;">Score '+score+'</span><br>'
    s += '<span>'+phrases+' phrases found in '+sources+' sources</span><br>';
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

function put_search_result(){
    var textData = document.getElementById("search_textarea").value;
    var solution = request_query_text(textData);
    console.log(solution);
    put_result_header(solution.score, solution.sources, solution.phrases);
    put_phrases(solution.phrase_hits);

}