var showMessage = function(object, msg) {
    var div = $('<div class="vote-notification"><h3>' + msg + '</h3>(Click the message box to close)</div>');

    div.click(function(event) {
        $(".vote-notification").fadeOut("fast", function() { $(this).remove(); });
    });

    object.parent().append(div);
    div.fadeIn("fast");
};

var notify = function() {
    var visible = false;
    return {
        show: function(html) {
            if (html) {
                $("body").css("margin-top", "2.2em");
                $(".notify span").html(html);        
            }          
            $(".notify").fadeIn("slow");
            visible = true;
        },       
        close: function(doPostback) {
            if (doPostback) {
               $.post("/messages/markread/", { formdata: "required" });
            }
            $(".notify").fadeOut("fast");
            $("body").css("margin-top", "0");
            visible = false;
        },     
        isVisible: function() { return visible; }     
    };
} ();

function appendLoader(containerSelector) {
    $(containerSelector).append('<img class="ajax-loader" src="/content/images/indicator.gif" title="Read in..." alt="Read in..." />');
}

function removeLoader() {
    $("img.ajax-loader").remove();
}

function setupFormValidation(formSelector, validationRules, validationMessages, onSubmitCallback) {
    enableSubmitButton(formSelector);
    $(formSelector).validate({
        rules: (validationRules ? validationRules : {}),
        messages: (validationMessages ? validationMessages : {}),
        errorElement: "span",
        errorClass: "form-error",
        errorPlacement: function(error, element) {
            var span = element.next().find("span.form-error");
            if (span.length == 0) {
                span = element.parent().find("span.form-error");
            }
            span.replaceWith(error);
        },
        submitHandler: function(form) {
            disableSubmitButton(formSelector);
            
            if (onSubmitCallback)
                onSubmitCallback();
            else
                form.submit();
        }
    });
}

function enableSubmitButton(formSelector) {
    setSubmitButtonDisabled(formSelector, false);
}
function disableSubmitButton(formSelector) {
    setSubmitButtonDisabled(formSelector, true);
}
function setSubmitButtonDisabled(formSelector, isDisabled) { 
    $(formSelector).find("input[type='submit']").attr("disabled", isDisabled ? "true" : "");    
}

var CPValidator = function(){
    return {
        getQuestionFormRules : function(){
            return {
                tags: {
                    required: true,
                    maxlength: 105
                },  
                text: {
                    required: true,
                    minlength: 10
                },
                title: {
                    required: true,
                    minlength: 10
                }
            };
        },
        getQuestionFormMessages: function(){
            return {
                tags: {
                    required: " Tags can not be empty。",
                    maxlength: " Up to five labels, each label is less than 20 characters in length."
                },
                text: {
                    required: " Content can not be empty.",
                    minlength: jQuery.format(" Please enter at least (10) characters.")
                },
                title: {
                    required: " Please enter a title.",
                    minlength: jQuery.format(" Please enter at least (10) characters.")
                }
            };
        }
    };
}();
