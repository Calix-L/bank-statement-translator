"""Legacy compatibility terms for garbled payment-related text."""

from __future__ import annotations

from typing import Dict


PAYMENT_INSTITUTION_TERMS: Dict[str, str] = {
    "鏀粯瀹?": "Alipay",
    "鏀粯瀹濓紙涓浗锛夌綉缁滄妧鏈湁闄愬叕鍙?": "Alipay (China) Network Technology Co Ltd",
    "鏀粯瀹?涓浗)缃戠粶鎶€鏈湁闄愬叕鍙?": "Alipay (China) Network Technology Co Ltd",
    "璐粯閫?": "Tenpay",
    "璐粯閫氭敮浠樼鎶€鏈夐檺鍏徃": "Tenpay Payment Technology Co Ltd",
    "娣卞湷甯傝储浠橀€氭敮浠樼鎶€鏈夐檺鍏徃": "Shenzhen Tenpay Payment Technology Co Ltd",
    "寰俊鏀粯": "WeChat Pay",
    "寰俊鏀粯鍟嗘埛骞冲彴": "WeChat Pay Merchant Platform",
    "缃戦摱鍦ㄧ嚎": "NetBank Online",
    "缃戦摱鍦ㄧ嚎锛堝寳浜級绉戞妧鏈夐檺鍏徃": "NetBank Online (Beijing) Technology Co Ltd",
    "缃戦摱鍦ㄧ嚎(鍖椾含)绉戞妧鏈夐檺鍏徃": "NetBank Online (Beijing) Technology Co Ltd",
    "缃戦摱鍦ㄧ嚎锛堝寳浜級鏀粯绉戞妧鏈夐檺鍏徃": "NetBank Online (Beijing) Payment Technology Co Ltd",
    "缃戦摱鍦ㄧ嚎(鍖椾含)鏀粯绉戞妧鏈夐檺鍏徃": "NetBank Online (Beijing) Payment Technology Co Ltd",
    "浜笢鏀粯": "JD Pay",
    "浜笢閽卞寘": "JD Wallet",
    "閾惰仈": "UnionPay",
    "涓浗閾惰仈": "China UnionPay",
    "浜戦棯浠?": "QuickPass",
    "閾惰仈浜戦棯浠?": "UnionPay QuickPass",
    "浜笢闂粯": "JD QuickPass",
    "鐧芥潯闂粯": "Baitiao QuickPass",
    "鎷夊崱鎷?": "Lakala",
    "鎷夊崱鎷夋敮浠樿偂浠芥湁闄愬叕鍙?": "Lakala Payment Corporation",
}


PAYMENT_CHANNEL_TERMS: Dict[str, str] = {
    "鎵爜": "Scan to Pay",
    "鎵爜鏀粯": "Scan Payment",
    "鎵爜鏀舵": "Scan Collection",
    "鎵爜浠樻": "Scan Payment",
    "浜岀淮鐮佹敹娆?": "QR Code Collection",
    "浜岀淮鐮佷粯娆?": "QR Code Payment",
    "浠樻鐮佹敮浠?": "Payment Code Payment",
    "鏉＄爜鏀粯": "Barcode Payment",
    "鍒峰崱": "Card Swipe",
    "鍒峰崱娑堣垂": "Card Consumption",
    "POS娑堣垂": "POS Purchase",
    "POS浜ゆ槗": "POS Transaction",
    "NFC鏀粯": "NFC Payment",
    "闂粯": "QuickPass",
    "鍒疯劯鏀粯": "Face Payment",
    "鏃犳劅鏀粯": "Seamless Payment",
    "灏忕▼搴忔敮浠?": "Mini Program Payment",
    "鍏紬鍙锋敮浠?": "Official Account Payment",
    "H5鏀粯": "H5 Payment",
    "APP鏀粯": "App Payment",
    "缃戝叧鏀粯": "Gateway Payment",
    "鍗忚鏀粯": "Agreement Payment",
    "鍏嶅瘑鏀粯": "Password-free Payment",
    "浠ｆ墸绛剧害": "Auto Debit Authorization",
    "鍟嗘埛鎵ｆ": "Merchant Debit",
}


PAYMENT_TERMS: Dict[str, str] = {
    "鐜伴噾": "Cash",
    "閾惰鍗?": "Bank Card",
    "淇＄敤鍗?": "Credit Card",
    "鍊熻鍗?": "Debit Card",
    "瀛樻姌": "Passbook",
    "瀛樺崟": "Certificate of Deposit",
    "鍙栨": "Withdrawal",
    "瀛樻": "Deposit",
    "鍒╂伅": "Interest",
    "骞磋垂": "Annual Fee",
    "鏈堣垂": "Monthly Fee",
    "鎵嬬画璐?": "Service Fee",
    "宸ユ湰璐?": "Processing Fee",
    "鐭俊楠岃瘉鐮?": "SMS Verification Code",
    "鍔ㄦ€佸彛浠?": "One-Time Password",
    "鍙屽洜绱犺璇?": "Two-Factor Authentication",
    "姹囩巼": "Exchange Rate",
    "璐眹": "FX Purchase",
    "缁撴眹": "FX Settlement",
    "鍞眹": "FX Sale",
}
