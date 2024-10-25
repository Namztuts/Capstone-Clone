const BASE_URL = '/api';

const $eventFormPopup = $('#eventFormPopup');
const $editEventFormPopup = $('#editEventFormPopup');
const $eventForm = $('#event-form');
const $editEventForm = $('#edit-event-form');

//fullCalendar initialization
$(document).ready(function () {
   $('#calendar').fullCalendar({
      selectable: true,
      //select is when a specific date is clicked on | this brings up a form to create an event for that date
      select: function (start, end, jsEvent) {
         let $closeBtn = $('#closePopup');

         //grab the date clicked and current time
         const clickedDate = moment(start).format('YYYY-MM-DD');
         const currentTime = moment().format('HH:mm');
         const dateTimeForInput = `${clickedDate}T${currentTime}`;
         //automatically fill the start/end times with the date clicked+current time
         $('#start_time').val(dateTimeForInput);
         $('#end_time').val(dateTimeForInput);

         //show the popup and position it relative to the clicked date | pageX & pageY are the click coordinates
         $($eventFormPopup).css({
            left: jsEvent.pageX + 'px',
            top: jsEvent.pageY + 'px',
            display: 'block',
         });

         //close popup with x
         $($closeBtn).on('click', function () {
            $($eventFormPopup).css({
               display: 'none',
            });
         });

         //close the form if clicked outside of the event form
         $(document).on('mousedown', function (e) {
            if (
               !$(e.target).closest($eventFormPopup).length &&
               $eventFormPopup.is(':visible')
            ) {
               $eventFormPopup.css({
                  display: 'none',
               });
            }
         });

         //event creation | .off ensures that eventlistener is not duplicating form submission data | shuts off any previous eventlisteners before starting
         $eventForm.off('submit').on('submit', async function (e) {
            e.preventDefault();

            //check if start time is before end time
            let startTime = $('#start_time').val();
            let endTime = $('#end_time').val();
            if (startTime > endTime) {
               alert('Start time must be before the end time.');
               return;
            }

            let formData = {
               title: $('#title').val(),
               description: $('#description').val(),
               start_time: $('#start_time').val(),
               end_time: $('#end_time').val(),
               location: $('#location').val(),
               bg_color: $('#bg_color').val(),
               txt_color: $('#txt_color').val(),
               all_day: $('#all_day').is(':checked'), //for Boolean checkbox
               creator_id: $('#creator_id').val(),
               calendar_id: $('#calendar_id').val(),
            };

            await axios
               .post(`${BASE_URL}/events`, formData)
               // .then runs if response is successful
               .then(function (response) {
                  let newEvent = response.data.event;
                  console.log('Event sent to DB', newEvent);

                  //adds visual to the calendar
                  $('#calendar').fullCalendar(
                     'renderEvent',
                     {
                        id: newEvent.id,
                        title: newEvent.title,
                        start: newEvent.start_time,
                        end: newEvent.end_time,
                        allDay: newEvent.all_day,
                        backgroundColor: newEvent.bg_color,
                        textColor: newEvent.txt_color,
                     },
                     true
                  );

                  //reset form fields | only resets on successful form submission
                  $eventForm[0].reset();
                  //hide the popup again
                  $($eventFormPopup).css({
                     display: 'none',
                  });
               })
               // .catch runs if response in NOT successful | display error in console and on screen for failed creation
               .catch(function (error) {
                  console.error('Error creating event:', error);
                  alert(
                     'There was an error creating the event. Please try again.'
                  );
               });
         });

         //clear the event form with the button
         $('#clearBtn')
            .off('click')
            .on('click', async function () {
               $eventForm[0].reset();
            });
      },
      //calendar header/footer/button formats
      header: {
         left: 'month, agendaWeek, agendaDay',
         center: 'title',
         right: 'prev, today, next',
      },
      buttonText: {
         today: 'Today',
         month: 'Month',
         week: 'Week',
         day: 'Day',
      },
      events: [], //empty array to add the events to | events in here are displayed on the calendar
      //eventClick is when a specific event is clicked | this brings up the edit event form
      eventClick: async function (event, jsEvent, view) {
         console.log('Clicked event >', event);
         let $closeBtn = $('#closeEditPopup');

         $($editEventFormPopup).css({
            left: jsEvent.pageX + 'px',
            top: jsEvent.pageY + 'px',
            display: 'block',
         });

         $($closeBtn).on('click', function () {
            $($editEventFormPopup).css({
               display: 'none',
            });
         });

         $(document).on('mousedown', function (e) {
            if (
               !$(e.target).closest($editEventFormPopup).length &&
               $editEventFormPopup.is(':visible')
            ) {
               $editEventFormPopup.css({
                  display: 'none',
               });
            }
         });

         const response = await axios.get(`${BASE_URL}/events/${event.id}`); //getting the event from the DB
         const dbEvent = response.data.event;
         console.log('DB event >', dbEvent);

         $('#edit_title').val(dbEvent.title);
         $('#edit_description').val(dbEvent.description);
         $('#edit_start_time').val(dbEvent.start_time);
         $('#edit_end_time').val(dbEvent.end_time);
         $('#edit_location').val(dbEvent.location);
         $('#edit_bg_color').val(dbEvent.bg_color);
         $('#edit_txt_color').val(dbEvent.txt_color);
         $('#edit_all_day').prop('checked', dbEvent.all_day);

         $editEventForm.off('submit').on('submit', async function (e) {
            e.preventDefault();

            //check if start time is before end time
            let startTime = $('#start_time').val();
            let endTime = $('#end_time').val();
            if (startTime > endTime) {
               alert('Start time must be before the end time.');
               return;
            }

            let formData = {
               title: $('#edit_title').val(),
               description: $('#edit_description').val(),
               start_time: $('#edit_start_time').val(),
               end_time: $('#edit_end_time').val(),
               location: $('#edit_location').val(),
               bg_color: $('#edit_bg_color').val(),
               txt_color: $('#edit_txt_color').val(),
               all_day: $('#edit_all_day').is(':checked'), //for Boolean checkbox
            };

            await axios.patch(`${BASE_URL}/events/${dbEvent.id}`, formData);

            //reset form fields | only resets on successful form submission
            $editEventForm[0].reset();
            //hide the popup again
            $($editEventFormPopup).css({
               display: 'none',
            });
         });

         //delete button to delete event
         $('#deleteEventBtn')
            .off('click')
            .on('click', async function () {
               const confirmDelete = confirm(
                  // browser alert to confirm the deletion
                  'Are you sure you want to delete this event?'
               );

               if (confirmDelete) {
                  try {
                     await axios.delete(`${BASE_URL}/events/${dbEvent.id}`);
                     //re render the events on the page and hide the popup
                     fetchAndRenderEvents($('#calendar_id').val());
                     $($editEventFormPopup).css({ display: 'none' });
                  } catch (error) {
                     alert(
                        'There was an error deleting the event. Please try again.'
                     );
                  }
               }
            });
      },
   });

   async function fetchAndRenderEvents(calId) {
      try {
         const response = await axios.get(
            `${BASE_URL}/calendars/${calId}/events`
         );
         const events = response.data.events;
         let eventsFormatted = [];

         //loop the events and change them into fullCalendar format
         events.forEach((event) => {
            eventsFormatted.push({
               id: event.id,
               //if an all_day event, add a star to the title
               title: event.all_day ? '* ' + event.title : event.title,
               //if the all_day box is checked, remove the time from the start/end times
               start: event.all_day
                  ? event.start_time.split('T')[0]
                  : event.start_time,
               end: event.all_day
                  ? event.end_time.split('T')[0]
                  : event.end_time,
               allDay: event.all_day,
               backgroundColor: event.bg_color,
               textColor: event.txt_color,
            });
         });
         console.log('Response >', response);
         console.log('Events >', eventsFormatted);
         $('#calendar').fullCalendar('removeEvents'); //clear any events
         $('#calendar').fullCalendar('renderEvents', eventsFormatted, true); //add events from DB :)
      } catch (error) {
         console.error('Error fetching events:', error);
      }
   }
   const calendarID = $('#calendar_id').val();
   fetchAndRenderEvents(calendarID);

   //change the calendar based on the select field
   $('#calendars').on('change', function () {
      const selectedCalendar = $(this).val();

      //changes to the updated calendar URL
      window.location.href = `/user/${$(
         '#creator_id'
      ).val()}/calendar/${selectedCalendar}`;

      fetchAndRenderEvents(selectedCalendar);
   });
});
