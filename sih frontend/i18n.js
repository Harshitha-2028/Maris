import i18next from 'i18next';

import { initReactI18next } from 'react-i18next';

  

i18next.use(initReactI18next).init({

resources: {

'en-IN': {

translation: {

login: 'Login',

email: 'Email',

password: 'Password',

voice_email: 'Voice Email',

voice_password: 'Voice Password',

login_button: 'Login',

login_success: 'Login successful',

login_failed: 'Login failed, try again',

admin_dashboard: 'Admin Dashboard',

project_id: 'Project ID',

metadata_cid: 'Metadata CID',

register_project: 'Register Project',

minter_dashboard: 'Minter Dashboard',

plot_id: 'Plot ID',

project_type: 'Project Type',

voice_input: '🎤 Voice Input',

upload_data: 'Upload Data',

user_dashboard: 'User Dashboard',

},

},

'hi-IN': {

translation: {

login: 'लॉगिन',

email: 'ईमेल',

password: 'पासवर्ड',

voice_email: 'वॉइस ईमेल',

voice_password: 'वॉइस पासवर्ड',

login_button: 'लॉगिन करें',

login_success: 'लॉगिन सफल',

login_failed: 'लॉगिन विफल, फिर से प्रयास करें',

admin_dashboard: 'एडमिन डैशबोर्ड',

project_id: 'प्रोजेक्ट आईडी',

metadata_cid: 'मेटाडेटा सीआईडी',

register_project: 'प्रोजेक्ट रजिस्टर करें',

minter_dashboard: 'मिन्टर डैशबोर्ड',

plot_id: 'प्लॉट आईडी',

project_type: 'प्रोजेक्ट प्रकार',

voice_input: '🎤 वॉइस इनपुट',

upload_data: 'डेटा अपलोड करें',

user_dashboard: 'उपयोगकर्ता डैशबोर्ड',

},

},

'bn-IN': {

translation: {

login: 'লগইন',

email: 'ইমেল',

password: 'পাসওয়ার্ড',

voice_email: 'ভয়েস ইমেল',

voice_password: 'ভয়েস পাসওয়ার্ড',

login_button: 'লগইন করুন',

login_success: 'লগইন সফল',

login_failed: 'লগইন ব্যর্থ, আবার চেষ্টা করুন',

admin_dashboard: 'অ্যাডমিন ড্যাশবোর্ড',

project_id: 'প্রজেক্ট আইডি',

metadata_cid: 'মেটাডেটা সিআইডি',

register_project: 'প্রজেক্ট নিবন্ধন করুন',

minter_dashboard: 'মিন্টার ড্যাশবোর্ড',

plot_id: 'প্লট আইডি',

project_type: 'প্রজেক্টের ধরন',

voice_input: '🎤 ভয়েস ইনপুট',

upload_data: 'ডেটা আপলোড করুন',

user_dashboard: 'ব্যবহারকারী ড্যাশবোর্ড',

},

},

},

lng: 'en-IN',

fallbackLng: 'en-IN',

});

  

export default i18next;