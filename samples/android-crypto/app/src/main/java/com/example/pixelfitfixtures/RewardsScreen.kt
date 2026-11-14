package com.example.pixelfitfixtures

import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clipToBounds
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp

private val Background = Color(0xFFF8F9FA)
private val Ink = Color(0xFF212529)
private val Muted = Color(0xFF6C757D)
private val Blue = Color(0xFF0063F5)

@Composable
fun RewardsScreen() {
    Box(Modifier.size(375.dp, 812.dp).background(Background).clipToBounds()) {
        StatusBar(Modifier.offset(x = 32.dp, y = 15.dp))
        SummaryCard("Coupons", listOf(
            Stat("No.of Coupons Won", "06"),
            Stat("Tokens won from Spin so far", "08", true),
            Stat("Remaining Coupons to Spin", "01", true)
        ), Modifier.offset(x = 16.dp, y = 64.dp).size(343.dp, 174.dp))
        SummaryCard("Referral", listOf(
            Stat("Total No of referral", "12"),
            Stat("Total No of Qualified referral", "05", true)
        ), Modifier.offset(x = 16.dp, y = 241.dp).size(343.dp, 137.dp))
        RewardBanner("Refer and Earn", "Refer you Friend\nand Win Cryptocoins", "Refer Now", Color(0xFFFF9800),
            R.drawable.reward_referral_art, 241, 42, 101, 103, Modifier.offset(x = 16.dp, y = 394.dp))
        RewardBanner("Rewards", "Like, Share\n& get free coupons", "Share Now", Color(0xFF9900F5),
            R.drawable.reward_share_art, 225, 66, 98, 77, Modifier.offset(x = 16.dp, y = 562.dp))
        BottomNavigation(Modifier.offset(y = 724.dp), selectedIndex = 2)
    }
}

private data class Stat(val label: String, val value: String, val highlighted: Boolean = false)

@Composable
private fun SummaryCard(title: String, stats: List<Stat>, modifier: Modifier = Modifier) {
    Column(modifier.background(Color.White, RoundedCornerShape(12.dp)).padding(start = 20.dp, end = 24.dp, top = 20.dp)) {
        Text(title, color = Ink, fontSize = 20.sp, fontWeight = FontWeight.Bold, lineHeight = 24.sp)
        Spacer(Modifier.height(16.dp))
        stats.forEach { stat ->
            Row(Modifier.fillMaxWidth().height(31.dp), horizontalArrangement = Arrangement.SpaceBetween) {
                Text(stat.label, color = Muted, fontSize = 12.sp, maxLines = 1)
                Text(stat.value, color = if (stat.highlighted) Blue else Ink, fontSize = 14.sp, fontWeight = FontWeight.Medium)
            }
        }
    }
}

@Composable
private fun RewardBanner(eyebrow: String, title: String, action: String, color: Color, illustration: Int, imageX: Int, imageY: Int, imageWidth: Int, imageHeight: Int, modifier: Modifier = Modifier) {
    Box(modifier.size(343.dp, 160.dp).background(color, RoundedCornerShape(12.dp)).clipToBounds()) {
        Image(painterResource(illustration), contentDescription = null, modifier = Modifier.offset(x = imageX.dp, y = imageY.dp).size(imageWidth.dp, imageHeight.dp))
        Text(eyebrow, Modifier.offset(x = 20.dp, y = 20.dp), color = Color.White, fontSize = 12.sp)
        Text(title, Modifier.offset(x = 20.dp, y = 45.dp), color = Color.White, fontSize = 18.sp, fontWeight = FontWeight.Medium, lineHeight = 23.sp)
        Box(Modifier.offset(x = 20.dp, y = 113.dp).height(31.dp).background(Background, RoundedCornerShape(4.dp)).padding(horizontal = 12.dp), contentAlignment = Alignment.Center) {
            Text(action, color = color, fontSize = 12.sp, maxLines = 1)
        }
    }
}
