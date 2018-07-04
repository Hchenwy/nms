//显示页面导航
function show_page_navi(page_id, page_max) {
    var item = "";

    if (typeof(page_max) == "undefined") {
        page_max = 1;
    }

    $('#page_navi').empty();
    if (page_id == 1) {
        item += '<li class="prev disabled"><a onclick="change_page(1)"><i class="icon-angle-left"></i></a></li>';
        item += '<li class="prev disabled"><a onclick="change_page(' + (page_id - 1) + ')"><i class="icon-double-angle-left"></i></a></li>';
    } else {
        item += '<li class="prev"><a onclick="change_page(1)"><i class="icon-angle-left"></i></a></li>';
        item += '<li class="prev"><a onclick="change_page(' + (page_id - 1) + ')"><i class="icon-double-angle-left"></i></a></li>';
    }

    if ( page_max <= 5) {
        for (var i=1; i<=page_max; i++) {
            if (i == page_id) {
                item += '<li class="active"><a onclick="change_page(' + i + ')">' + i + '</a></li>';
            } else {
                item += '<li><a onclick="change_page(' + i + ')">' + i + '</a></li>';
            }
        }
    } else {
        if ( page_id <= 3) {
            for (var i=1; i<=5; i++) {
                if (i == page_id) {
                    item += '<li class="active"><a onclick="change_page(' + i + ')">' + i + '</a></li>';
                } else {
                    item += '<li><a onclick="change_page(' + i + ')">' + i + '</a></li>';
                }
            }
        } else if (page_max - page_id <= 2) {
            for (var i=page_max - 4; i<=page_max; i++) {
                if (i == page_id) {
                    item += '<li class="active"><a onclick="change_page(' + i + ')">' + i + '</a></li>';
                } else {
                    item += '<li><a onclick="change_page(' + i + ')">' + i + '</a></li>';
                }
            }
        } else {
            for (var i=page_id - 2; i<=page_id + 2; i++) {
                if (i == page_id) {
                    item += '<li class="active"><a onclick="change_page(' + i + ')">' + i + '</a></li>';
                } else {
                    item += '<li><a onclick="change_page(' + i + ')">' + i + '</a></li>';
                }
            }
        }
    }

    if (page_id == page_max) {
        item += '<li class="next disabled"><a onclick="change_page(' + (page_id + 1) + ')"><i class="icon-double-angle-right"></i></a></li>';
        item += '<li class="next disabled"><a onclick="change_page(' + page_max + ')"><i class="icon-angle-right"></i></a></li>';
    } else {
        item += '<li class="next"><a onclick="change_page(' + (page_id + 1) + ')"><i class="icon-double-angle-right"></i></a></li>';
        item += '<li class="next"><a onclick="change_page(' + page_max + ')"><i class="icon-angle-right"></i></a></li>';
    }
    $('#page_navi').append(item);
}
//显示分页图标
function show_sel_icon() {
    var sel_icon = '每页<select  id="sel_size" size="1" name="sample-table-2_length" aria-controls="sample-table-2"><option value="10">10</option><option value="20">20</option><option value="50">50</option><option value="100">100</option></select>条记录&nbsp;&nbsp;'
    $('#sel_icon').empty();
    $('#sel_icon').append(sel_icon);
}
//显示节点总数
function show_node_num(node_num) {
    if (typeof(node_num) == "undefined") {
        node_num = 0;
    }

    var num_str = '共 ' + node_num +  ' 条';
    $('#node_num').empty();
    $('#node_num').append(num_str);
}
