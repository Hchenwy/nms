function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                // break;
            }
        }
    }
    return cookieValue;
}


function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

function setAjaxCSRFToken() {
    var csrftoken = getCookie('csrftoken');
    var sessionid = getCookie('sessionid');

    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });
}



function activeNav() {
    var url_array = document.location.pathname.split("/");
    var app = url_array[1];
    var resource = url_array[2];
    if (app == '') {
        $('#index').addClass('active');
    } else {
        $("#" + app).addClass('active');
        $('#' + app + ' #' + resource).addClass('active');
    }
}

function APIUpdateAttr(props) {
    // props = {url: .., body: , success: , error: , method: ,}
    props = props || {};
    var success_message = props.success_message || 'Update Successfully!';
    var fail_message = props.fail_message || 'Error occurred while updating.';
    $.ajax({
        url: props.url,
        type: props.method || "PATCH",
        data: props.body,
        contentType: props.content_type || "application/json; charset=utf-8",
        dataType: props.data_type || "json"
    }).done(function (data, textStatue, jqXHR) {
        toastr.success(success_message);
        if (typeof props.success === 'function') {
            return props.success(data);
        }

    }).fail(function (jqXHR, textStatue, errorThrown) {
        toastr.error(fail_message);
        if (typeof props.error === 'function') {
            return props.error(errorThrown);
        }
    });
    // return true;
}


function objectDelete(obj, name, url, redirectTo) {
    function doDelete() {
        var body = {};
        var success = function () {
            swal('删除!', "[ " + name + "]" + " 已经被删除 ", "success");
            if (!redirectTo) {
                $(obj).parent().parent().parent().remove();
            } else {
                window.location.href = redirectTo;
            }
        };
        var fail = function () {
            swal("失败", "删除" + "[ " + name + " ]" + "失败", "error");
        };
        APIUpdateAttr({
            url: url,
            body: JSON.stringify(body),
            method: 'DELETE',
            success: success,
            error: fail
        });
    }
    swal({
        title: '确认删除 ?',
        text: " [" + name + "] ",
        type: "warning",
        showCancelButton: true,
        cancelButtonText: '取消',
        confirmButtonColor: "#DD6B55",
        confirmButtonText: '确认',
        closeOnConfirm: false
    }, function () {
        doDelete()
    });
}

function doDelete(the_url, plain_id_list) {
    var del_num = plain_id_list.length;
    swal({
        title: "你确认吗?",
        text: "删除选中的" + del_num + "个目标!!!",
        type: "warning",
        showCancelButton: true,
        confirmButtonColor: "#DD6B55",
        confirmButtonText: "确认",
        closeOnConfirm: false
    }, function() {
        var success = function() {
            var msg = "已被删除";
            swal("删除", msg, "success");
            $(".select-item input[type=checkbox]:checked").each(function() {
                jQuery(this).parent().parent().parent().parent().remove();
            });
        };
        var fail = function() {
            var msg = "删除失败";
            swal("删除", msg, "error");
        };
        var url_delete = the_url + '?id__in=' + JSON.stringify(plain_id_list);
        APIUpdateAttr({url: url_delete, method: 'DELETE', success: success, error: fail});
    });
}

function hiden_col(dt_api, col_num) {
        for (var i=0;i<col_num;i++) {
          dt_api.column(i).visible(0);
        };
        $("a.toggle-vis").removeClass("active");
}

function show_col(dt_api, show_col) {
        for (var i=0;i<show_col.length;i++) {
          dt_api.column(show_col[i]).visible(1);
        };
         $("a.default-col").addClass("active");
}

function chosen_col(dt_api) {
        $('a.toggle-vis').on( 'click', function (e) {
            e.preventDefault();
            // Get the column API object
            // alert( $(this).attr('data-column') );
            var column = dt_api.column( $(this).attr('data-column') );
 
            // Toggle the visibility
            column.visible( ! column.visible() );
        } );
}

//check/uncheck all messages
$('#id-toggle-all').removeAttr('checked').on('click', function(){
	if(this.checked) {
		CheckTable.select_all();
	} else CheckTable.select_none();
});

//select all
$('#id-select-all').on('click', function(e) {
	e.preventDefault();
	CheckTable.select_all();
});

//select none
$('#id-select-none').on('click', function(e) {
	e.preventDefault();
	CheckTable.select_none();
});


var CheckTable = {
	select_all : function() {
		$('.select-item input[type=checkbox]').each(function(){
			this.checked = true;
			$(this).closest('.select-item').addClass('selected');
		});
		
		$('#id-toggle-all').get(0).checked = true;		
	}
	,
	select_none : function() {
		$('.select-item input[type=checkbox]').removeAttr('checked').closest('.select-item').removeClass('selected');
		$('#id-toggle-all').get(0).checked = false;
	}
}