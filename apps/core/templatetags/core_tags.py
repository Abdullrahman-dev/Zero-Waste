from django import template
from django.utils.translation import get_language

register = template.Library()

# Simple translation dictionary for core UI elements
TRANSLATIONS = {
    'en': {
        'الإعدادات': 'Settings',
        'الملف الشخصي': 'Profile',
        'اسم المستخدم (Username)': 'Username',
        'حفظ التغييرات': 'Save Changes',
        'اللغة': 'Language',
        'العربية': 'Arabic',
        'English': 'English',
        'المظهر': 'Appearance',
        'الوضع الداكن (Dark Mode)': 'Dark Mode',
        'الأمان': 'Security',
        'استعادة كلمة المرور': 'Reset Password',
        'Zero Waste': 'Zero Waste',
        'وضع المشاهدة': 'Impersonation Mode',
        'العودة للأدمن 🔙': 'Back to Admin 🔙',
        'لوحة التحكم': 'Dashboard',
        'ربط الأنظمة': 'Integrations',
        'إضافة منتج جديد': 'Add New Product',
        'إضافة للمخزون': 'Add Stock',
        'المخزون': 'Inventory',
        'سجل الهدر': 'Waste Logs',
        'الفروع': 'Branches',
        'التحليلات': 'Analytics',
        'العمليات': 'Operations',
        'تسجيل خروج': 'Logout',
        'تحليل الهدر (آخر العمليات)': 'Waste Analysis (Recent)',
        'مركز الإشعارات': 'Notifications Center',
        'تحليل جديد': 'New Analysis',
        'إدارة الفروع': 'Manage Branches',
        'إضافة فرع جديد': 'Add New Branch',
        'الفروع النشطة': 'Active Branches',
        'إجمالي الهدر المالي': 'Total Waste Cost',
        'طلبات معلقة': 'Pending Requests',
        'نقص مخزون': 'Low Stock',
        'الكمية الحالية': 'Current Quantity',
        'الحد الأدنى': 'Minimum Quantity',
        'يرجى إعادة التموين': 'Restock needed',
        'لا توجد إشعارات أو تنبيهات': 'No notifications or alerts',
        'تاريخ التقرير': 'Report Date',
        'قيمة الهدر': 'Waste Value',
        'التفاصيل': 'Details',
        'عرض': 'View',
        'طلبات الفروع': 'Branch Orders',
        'طلباتي المرسلة': 'My Sent Requests',
        'موافقة': 'Approve',
        'جميع الطلبات معالجة': 'All requests processed',
        'انتظار': 'Pending',
        'مقبول': 'Approved',
        'مرفوض': 'Rejected',
        'لم يتم إرسال أي طلبات.': 'No requests sent.',
        'طلب جديد': 'New Request',
        'مركز تحليلات الذكاء الاصطناعي': 'AI Analysis Center',
        'لا توجد تحليلات ذكية حالياً': 'No smart analysis currently',
        'اختر فرعاً واضغط "تحليل" لاكتشاف فرص تقليل الهدر': 'Choose a branch and click "Analyze" to discover waste reduction opportunities',
        'جاري تحليل البيانات...': 'Analyzing data...',
        'يقوم الذكاء الاصطناعي بمراجعة سجلات الهدر والمخزون': 'AI is reviewing waste and inventory logs',
        'توزيع المخاطر حسب الفئة': 'Risk distribution by category',
        'الأصناف الأكثر عرضة للهدر (7 أيام)': 'Items most at risk of waste (7 days)',
        'التوصيات الذكية': 'Smart Recommendations',
        'قيمة الهدر المتوقع': 'Expected Waste Value',
        'اختر النطاق للتحليل': 'Select Scope for Analysis',
        'حدد الفرع الذي تريد من الذكاء الاصطناعي تحليل بياناته': 'Identify the branch you want the AI to analyze its data',
        'كل الشركة (تحليل شامل)': 'All Company (Comprehensive Analysis)',
        'إلغاء': 'Cancel',
        'ابدأ التحليل 🚀': 'Start Analysis 🚀',
        'طلباتي المرسلة': 'Sent Requests',
        'تحليل الذكاء الاصطناعي - Zero Waste': 'AI Analysis - Zero Waste',
        'تقارير الذكاء الاصطناعي': 'AI Reports',
        'المستشار الذكي ✨': 'Smart Advisor ✨',
        'أكثر المنتجات هدراً هذا الشهر': 'Most Wasted Items This Month',
        'الخسائر المالية (آخر 6 شهور)': 'Financial Losses (Last 6 Months)',
        'توقعات تقليل الكميات (للتحكم في الفائض)': 'Quantity Reduction Forecasts (Excess Control)',
        'احصل على خطة مفصلة لتقليل مشتريات الأسبوع القادم وتقليل الخسائر.': 'Get a detailed plan to reduce next week\'s purchases and minimize losses.',
        'عرض توصيات الشراء': 'View Purchase Recommendations',
        'سجل التقارير السابقة': 'Previous Reports Log',
        'رقم التقرير': 'Report ID',
        'الفرع': 'Branch',
        'تاريخ التحليل': 'Analysis Date',
        'القيمة المهددة': 'Threatened Value',
        'الحالة': 'Status',
        'إجراء سريع': 'Quick Action',
        'تفعيل خصم': 'Activate Discount',
        'تبرع': 'Donate',
        'لا توجد تقارير حالياً': 'No reports currently',
        'سجل الهدر - Zero Waste': 'Waste Log - Zero Waste',
        'سجل الهدر والخسائر': 'Waste and Loss Log',
        'متابعة دقيقة لكل ما يتم هدره في الفرع': 'Careful tracking of everything wasted in the branch',
        'تسجيل هدر جديد': 'Log New Waste',
        'التاريخ': 'Date',
        'المنتج': 'Product',
        'الكمية': 'Quantity',
        'السبب': 'Reason',
        'المسؤول': 'Person in Charge',
        'ملاحظات': 'Notes',
        'ممتاز! لا يوجد هدر مسجل.': 'Excellent! No waste logged.',
        'سجل المخزون - Zero Waste': 'Inventory Log - Zero Waste',
        'سجل المخزون الحالي': 'Current Inventory Log',
        'إضافة مخزون': 'Add Stock',
        'المنتج / SKU': 'Product / SKU',
        'تاريخ الانتهاء': 'Expiry Date',
        'الأيام المتبقية': 'Days Remaining',
        'الإجراءات': 'Actions',
        'ينتهي اليوم!': 'Expires Today!',
        'باقي': 'Remaining',
        'يوم': 'day',
        'أيام': 'days',
        'تالف / خطر': 'Damaged / Risk',
        'وشك الانتهاء': 'Near Expiry',
        'سليم': 'Safe',
        'المخزون فارغ حالياً': 'Inventory is currently empty',
        'إضافة أول منتج': 'Add First Product',
        'تعديل': 'Edit',
        'تسجيل كهدر': 'Log as Waste',
        'حذف نهائي': 'Final Delete',
        'منتهي منذ': 'Expired since',
        'إدارة العمليات - Zero Waste': 'Operations Management - Zero Waste',
        '📝 مركز التقارير والطلبات': '📝 Reports and Requests Center',
        'متابعة الطلبات التشغيلية والتواصل مع الإدارة': 'Follow up on operational requests and communicate with management',
        'رفع تقرير جديد': 'Submit New Report',
        'الكل': 'All',
        'قيد الانتظار': 'Pending',
        'مقبول': 'Approved',
        'مرفوض': 'Rejected',
        'كل الشركات': 'All Companies',
        'كل الفروع': 'All Branches',
        'رقم الطلب': 'Order Number',
        'العنوان': 'Title',
        'رد الإدارة': 'Management Response',
        'الإجراء': 'Action',
        'عرض': 'View',
        'قيد المراجعة': 'In Review',
        'تمت الموافقة': 'Approved',
        'موافق': 'Approve',
        'رفض': 'Reject',
        'رد': 'Reply',
        'لا توجد تقارير حالياً.': 'No reports currently.',
        'تفاصيل التقرير': 'Report Details',
        'إغلاق': 'Close',
        'إرسال التقرير': 'Send Report',
        '💬 رد على التقرير': '💬 Reply to Report',
        'اكتب ردك هنا...': 'Type your reply here...',
        'موافق ورد': 'Approve and Reply',
        'إرسال الرد فقط': 'Send Reply Only',
        'حفظ البيانات': 'Save Data',
        'إلغاء وعودة': 'Cancel and Back',
        'إضافة عنصر مخزون': 'Add Stock Item',
        'تعديل: ': 'Edit: ',
        'تسجيل هدر - Zero Waste': 'Log Waste - Zero Waste',
        'تسجيل عنصر تالف/مهدر': 'Log Damaged/Wasted Item',
        'تنبيه: سيتم خصم الكمية المسجلة من المخزون فوراً.': 'Warning: Recorded quantity will be deducted from inventory immediately.',
        'تسجيل الهدر': 'Log Waste',
        'إدارة الفروع - Zero Waste': 'Manage Branches - Zero Waste',
        '🏢 فروع المطعم': '🏢 Restaurant Branches',
        'اسم الفرع': 'Branch Name',
        'الموقع': 'Location',
        'المدير المسؤول': 'Responsible Manager',
        'حد الهدر': 'Waste Threshold',
        '-- غير محدد --': '-- Not Specified --',
        'لا توجد فروع مسجلة حالياً.': 'No branches currently registered.',
        '🏢 إضافة فرع جديد': '🏢 Add New Branch',
        'بيانات مدير الفرع الجديد (إجباري)': 'New Branch Manager Details (Mandatory)',
        'حفظ الفرع': 'Save Branch',
        'ربط الأنظمة (Integrations)': 'Integrations',
        '🔌 ربط الأنظمة (Integrations)': '🔌 Integrations',
        'إدارة الربط مع أنظمة نقاط البيع والمحاسبة.': 'Manage integrations with POS and accounting systems.',
        'تحديث الحالة': 'Refresh Status',
        'متصل (Connected)': 'Connected',
        'نظام فودكس (POS)': 'Foodics (POS)',
        'يتم سحب المبيعات والمخزون والمنتجات تلقائياً.': 'Sales, inventory, and products are automatically pulled.',
        'آخر تحديث: ': 'Last update: ',
        'إعدادات': 'Settings',
        'إضافة نظام جديد': 'Add New Integration',
        'سجل العمليات الأخيرة (Sync Log)': 'Recent Operations Log (Sync Log)',
        'النظام': 'System',
        'العملية': 'Operation',
        'الوقت': 'Time',
        'التفاصيل': 'Details',
        'لا توجد عمليات مؤخراً': 'No recent operations',
        'قبل دقيقتين': 'Two minutes ago',
        'تأكيد الحذف': 'Confirm Delete',
        '⚠️ تأكيد الحذف': '⚠️ Confirm Delete',
        'هل أنت متأكد أنك تريد حذف مخزون: ': 'Are you sure you want to delete stock: ',
        'لا يمكن التراجع عن هذه العملية.': 'This operation cannot be undone.',
        'نعم، احذف': 'Yes, delete',
        'تراجع': 'Back',
        'تسجيل الدخول - Zero Waste': 'Login - Zero Waste',
        'مرحباً بك مجدداً': 'Welcome Back',
        'خطأ في اسم المستخدم أو كلمة المرور': 'Error in username or password',
        'اسم المستخدم': 'Username',
        'كلمة المرور': 'Password',
        'تسجيل الدخول': 'Login',
        'للإنضمام، يرجى التواصل مع الإدارة': 'To join, please contact management',
    }
}

@register.filter
def smart_trans(value):
    lang = get_language()
    if lang == 'en' and value in TRANSLATIONS['en']:
        return TRANSLATIONS['en'][value]
    return value
