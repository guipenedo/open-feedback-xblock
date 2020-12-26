function OpenFeedbackXBlock(runtime, element, context) {
    let id = context.xblock_id;

    $(element).find('#submit_' + id).bind('click', function() {
        const data = {
            'student_feedback': $(element).find('#student_feedback_' + id).val()
        };
        const handlerUrl = runtime.handlerUrl(element, 'submit_feedback');
        $.post(handlerUrl, JSON.stringify(data)).done(() => {
            $(element).find('#of-input-group_' + id).replaceWith($('<p>Obrigado pelo feedback.</p>'));
        });
    });
}
