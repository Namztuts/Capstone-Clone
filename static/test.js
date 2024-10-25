$('#calendar').fullCalendar({
   selectable: true,
   editable: true, // Allow dragging and resizing of events
   events: '/api/events', // Your events API

   // Triggered when an event is clicked
   eventClick: function (event, jsEvent, view) {
      // Open a form or a modal for editing
      let $tooltip = $('#editEventTooltip'); // Assuming you have a form in a popup/modal for editing

      // Populate form fields with event data
      $('#edit_title').val(event.title);
      $('#edit_description').val(event.description);
      $('#edit_start_time').val(moment(event.start).format('YYYY-MM-DDTHH:mm')); // For datetime-local input
      $('#edit_end_time').val(moment(event.end).format('YYYY-MM-DDTHH:mm'));
      $('#edit_location').val(event.location);
      $('#edit_bg_color').val(event.bg_color);
      $('#edit_txt_color').val(event.txt_color);
      $('#edit_all_day').prop('checked', event.allDay);

      // Show the form near the clicked event
      $tooltip.css({
         left: jsEvent.pageX + 'px',
         top: jsEvent.pageY + 'px',
         display: 'block',
      });

      // Handle the form submission
      $('#editEventForm')
         .off('submit')
         .on('submit', function (e) {
            e.preventDefault();

            // Gather updated form data
            let updatedEventData = {
               title: $('#edit_title').val(),
               description: $('#edit_description').val(),
               start_time: $('#edit_start_time').val(),
               end_time: $('#edit_end_time').val(),
               location: $('#edit_location').val(),
               bg_color: $('#edit_bg_color').val(),
               txt_color: $('#edit_txt_color').val(),
               all_day: $('#edit_all_day').is(':checked'),
            };

            // Send update request to your server (API endpoint for updating the event)
            axios
               .patch(`/events/${event.id}`, updatedEventData)
               .then(function (response) {
                  // Update event on the calendar
                  event.title = updatedEventData.title;
                  event.start = updatedEventData.start_time;
                  event.end = updatedEventData.end_time;
                  event.location = updatedEventData.location;
                  event.backgroundColor = updatedEventData.bg_color;
                  event.textColor = updatedEventData.txt_color;
                  event.allDay = updatedEventData.all_day;

                  // Render updated event
                  $('#calendar').fullCalendar('updateEvent', event);

                  // Hide the popup/modal
                  $tooltip.css({ display: 'none' });

                  alert('Event updated successfully!');
               })
               .catch(function (error) {
                  console.error('Error updating event:', error);
                  alert('There was an error updating the event.');
               });
         });
   },
});
