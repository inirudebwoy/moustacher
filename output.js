var page = require('webpage').create();
page.open('file://{{template_path}}', function() {
  page.render('output.jpg', {format: 'jpeg', quality: '90'});
  phantom.exit();
});
