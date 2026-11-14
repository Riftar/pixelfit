package com.example.pixelfitfixtures

import android.graphics.Color
import android.graphics.drawable.GradientDrawable
import android.view.LayoutInflater
import android.view.View
import android.widget.ImageView
import android.widget.FrameLayout
import android.widget.LinearLayout
import android.widget.TextView

internal fun MainActivity.showRewardsXml() {
    setContentView(R.layout.rewards_screen)
    fun summary(id: Int, title: String, rows: List<Triple<String, String, Boolean>>) {
        val card = findViewById<View>(id)
        card.findViewById<TextView>(R.id.summary_title).text = title
        val container = card.findViewById<LinearLayout>(R.id.summary_rows)
        rows.forEach { (label, value, highlight) ->
            val row = LayoutInflater.from(this).inflate(R.layout.reward_stat_row, container, false)
            row.findViewById<TextView>(R.id.stat_label).text = label
            row.findViewById<TextView>(R.id.stat_value).apply {
                text = value
                setTextColor(Color.parseColor(if (highlight) "#0063F5" else "#212529"))
            }
            container.addView(row)
        }
    }
    fun banner(id: Int, eyebrow: String, title: String, action: String, hex: String, artwork: Int, imageX: Int, imageY: Int, imageWidth: Int, imageHeight: Int) {
        val banner = findViewById<View>(id)
        banner.background = GradientDrawable().apply {
            shape = GradientDrawable.RECTANGLE
            cornerRadius = 12 * resources.displayMetrics.density
            setColor(Color.parseColor(hex))
        }
        val density = resources.displayMetrics.density
        banner.findViewById<ImageView>(R.id.banner_illustration).apply {
            setImageResource(artwork)
            layoutParams = FrameLayout.LayoutParams((imageWidth * density).toInt(), (imageHeight * density).toInt()).apply {
                leftMargin = (imageX * density).toInt()
                topMargin = (imageY * density).toInt()
            }
        }
        banner.findViewById<TextView>(R.id.banner_eyebrow).text = eyebrow
        banner.findViewById<TextView>(R.id.banner_title).text = title
        banner.findViewById<TextView>(R.id.banner_action).apply {
            text = action
            setTextColor(Color.parseColor(hex))
        }
    }
    summary(R.id.coupons_card, "Coupons", listOf(
        Triple("No.of Coupons Won", "06", false),
        Triple("Tokens won from Spin so far", "08", true),
        Triple("Remaining Coupons to Spin", "01", true)
    ))
    summary(R.id.referral_card, "Referral", listOf(
        Triple("Total No of referral", "12", false),
        Triple("Total No of Qualified referral", "05", true)
    ))
    banner(R.id.referral_banner, "Refer and Earn", "Refer you Friend\nand Win Cryptocoins", "Refer Now", "#FF9800", R.drawable.reward_referral_art, 241, 42, 101, 103)
    banner(R.id.share_banner, "Rewards", "Like, Share\n& get free coupons", "Share Now", "#9900F5", R.drawable.reward_share_art, 225, 66, 98, 77)
    val nav = findViewById<android.widget.FrameLayout>(R.id.rewards_nav)
    val labels = nav.getChildAt(0) as LinearLayout
    (labels.getChildAt(0) as TextView).setTextColor(Color.parseColor("#6C757D"))
    (labels.getChildAt(2) as TextView).setTextColor(Color.parseColor("#0063F5"))
}
