from django.contrib import admin
from django.urls import path
from portal.views import AdminView, AdminLoginView, CreateAdminView, CreatingAdminListView, CreatingAdminSearchView, ChangeAdminStatusView, SignupLimoUserView, LoginLimoUserView, GetLimoUserDetailsView, LimoUserSearchView, CreateBookingView, GetBookingDetailsView, GenerateOTPAPI, VerifyOTPView, LimoDriverSignupView, PostPicturesView, GetDriverDataView, get_driver_image, LimoDriverSearchView, ChangeDriverStatusView, ApprovedDriversView, UnApprovedDriversView, UpdateBookingPrice, SendBookingBill, LoginLimoDriverView, ChangeDriverStatus, UpdateDriverLocation, GetOnlineDrivers, UpdateDriverName, CalculateEstimatedTime, GetCarInfoView, GetDriverInfoView, SubmitDriverReview, CheckBookingView, GettebView, SearchtebView, GetNotificationsByEmail, VerifyUserEmail, ForgotPasswordUser, GetBookingsByDriver, StartRide, VerifyEmailAndCheckBooking, UpdateBookinglink, UpdatePaymentStatus, UpdateRideStatus, VerifyOTPFPView, UserMessageAPIView, GetUnrepliedMessagesView, PostReplyView, GetUserMessagesView, GetDriverReviewsView, AddToTotalEarning, GetUserinfoDetails, UpdateUserDetails, DriverpickupCoordinates, UpdateDriverdestinationCoordinates, EndRide, GetDriverTravellingHistory, GetUserTravellingHistory, GetDriverTotalEarning, UpdateRideStatusafterpickup, VerifyDriverEmailAndCheckBooking, GetNotificationsByDriverEmail, GetDriverReviews, CheckOngoingRide

urlpatterns = [
    path('admin/', admin.site.urls),
    path('admin1/', AdminView.as_view()),
    path('adminlogin/', AdminLoginView.as_view()),
    path('creatingadmin/', CreateAdminView.as_view()),
    path('getnewadmin/', CreatingAdminListView.as_view()),
    path('searchadmin/', CreatingAdminSearchView.as_view()),
    path('cadminstatus/', ChangeAdminStatusView.as_view()),
    path('usersignup/', SignupLimoUserView.as_view()),
    path('getuser/', GetLimoUserDetailsView.as_view()),
    path('searchuser/', LimoUserSearchView.as_view()),
    path('loginuser/', LoginLimoUserView.as_view()),
    path('createbooking/', CreateBookingView.as_view()),
    path('getbooking/', GetBookingDetailsView.as_view()),
    path('sendotp/', GenerateOTPAPI.as_view()),
    path('verifyotp/', VerifyOTPView.as_view()),
    path('driversignup/', LimoDriverSignupView.as_view()),
    path('pictureupload/', PostPicturesView.as_view()),
    path('driver/<str:folder>/<str:filename>/', get_driver_image),
    path('getdriver/', GetDriverDataView.as_view()),
    path('searchdriver/', LimoDriverSearchView.as_view()),
    path('driverstatus/', ChangeDriverStatusView.as_view()),
    path('approved/', ApprovedDriversView.as_view()),
    path('unapproved/', UnApprovedDriversView.as_view()),
    path('price/', UpdateBookingPrice.as_view()),
    path('sendbill/', SendBookingBill.as_view()),
    path('driverlogin/', LoginLimoDriverView.as_view()),
    path('statusdriver/', ChangeDriverStatus.as_view()),
    path('driverlocation/', UpdateDriverLocation.as_view()),
    path('getactivedrivers/', GetOnlineDrivers.as_view()),
    path('updatedrivername/', UpdateDriverName.as_view()),
    path('estimatedtime/', CalculateEstimatedTime.as_view()),
    path('carinfo/', GetCarInfoView.as_view()),
    path('destapi/', GetDriverInfoView.as_view()),
    path('review/', SubmitDriverReview.as_view()),
    path('checkbooking/', CheckBookingView.as_view()),
    path('getteb/', GettebView.as_view()),
    path('searchteb/', SearchtebView.as_view()),
    path('getnoti/', GetNotificationsByEmail.as_view()),
    path('verifyemail/', VerifyUserEmail.as_view()),
    path('fpuser/', ForgotPasswordUser.as_view()),
    path('driverbooking/', GetBookingsByDriver.as_view()),
    path('startride/', StartRide.as_view()),
    path('gpstrackingcheck/', VerifyEmailAndCheckBooking.as_view()),
    path('link/', UpdateBookinglink.as_view()),
    path('paymentstatus/', UpdatePaymentStatus.as_view()),
    path('ridestatus/', UpdateRideStatus.as_view()),
    path('verifyotpfp/', VerifyOTPFPView.as_view()),
    path('sendmessage/', UserMessageAPIView.as_view()),
    path('admingetmessage/', GetUnrepliedMessagesView.as_view()),
    path('adminpostreply/', PostReplyView.as_view()),
    path('getusermessage/', GetUserMessagesView.as_view()),
    path('getreview/', GetDriverReviewsView.as_view()),
    path('addearning/', AddToTotalEarning.as_view()),
    path('userinfo/', GetUserinfoDetails.as_view()),
    path('upusde/', UpdateUserDetails.as_view()),
    path('driverpickup/', DriverpickupCoordinates.as_view()),
    path('driverdestination/', UpdateDriverdestinationCoordinates.as_view()),
    path('endride/', EndRide.as_view()),
    path('driverth/', GetDriverTravellingHistory.as_view()),
    path('userth/', GetUserTravellingHistory.as_view()),
    path('wallet/', GetDriverTotalEarning.as_view()),
    path('customerincar/', UpdateRideStatusafterpickup.as_view()),
    path('drivergpstrackingcheck/', VerifyDriverEmailAndCheckBooking.as_view()),
    path('drivernoti/', GetNotificationsByDriverEmail.as_view()),
    path('getdriverreview/', GetDriverReviews.as_view()),
    path('checkongoingride/', CheckOngoingRide.as_view()),
]

