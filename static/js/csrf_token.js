function getCookie(name)
{
    var arr,reg=new RegExp("(^| )"+name+"=([^;]*)(;|$)");

    if(arr=document.cookie.match(reg))

        return unescape(arr[2]);
    else
        return null;
}
$.ajaxSetup({
        headers: { "X-CSRFToken": getCookie("csrftoken") }
});