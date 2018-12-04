$('#popoverOption').popover({ trigger: "hover" });
$('dd').filter(':nth-child(n)').addClass('hide');
$('dl').on('click', 'dt', function() {
    $(this).next().slideToggle(200);
});
$('[data-toggle="tooltip"]').tooltip()