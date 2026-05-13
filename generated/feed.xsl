<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<xsl:output method="html" version="1.0" encoding="UTF-8" indent="yes"/>
<xsl:template match="/rss/channel">
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title><xsl:value-of select="title"/> RSS feed</title>
<meta name="description" content="RSS feed for PURSUE UFO Tracker. Subscribe in your reader to get every new file indexed within hours of release from war.gov."/>
<meta name="robots" content="noindex,follow"/>
<link rel="preconnect" href="https://fonts.googleapis.com"/>
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin="anonymous"/>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;700&amp;family=JetBrains+Mono:wght@400;700&amp;display=swap" rel="stylesheet"/>
<link rel="stylesheet" href="/styles.css"/>
<style>
.feed-page{max-width:880px;margin:0 auto;padding:60px 24px}
.feed-page h1{font-size:clamp(32px,4.5vw,52px);background:linear-gradient(180deg,#fff,#52b4ff);-webkit-background-clip:text;background-clip:text;color:transparent;margin-bottom:14px}
.feed-page .lede{font-size:18px;color:#dfe6ef;line-height:1.75;margin-bottom:32px}
.reader-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px;margin-bottom:48px}
.reader-grid a{display:block;padding:14px 18px;background:rgba(82,180,255,.06);border:1px solid rgba(82,180,255,.25);border-radius:8px;color:#dfe6ef;text-decoration:none;font-size:14px;text-align:center;transition:border-color .2s}
.reader-grid a:hover{border-color:#52b4ff}
.reader-grid a strong{display:block;color:#52b4ff;font-size:13px;margin-bottom:4px;font-family:'JetBrains Mono',monospace;letter-spacing:1px;text-transform:uppercase}
.feed-url{background:rgba(0,0,0,.3);border:1px solid rgba(82,180,255,.15);padding:12px 16px;border-radius:6px;font-family:'JetBrains Mono',monospace;font-size:13px;color:#52ffb4;margin:16px 0 32px;word-break:break-all}
.entry{padding:24px;background:rgba(10,15,28,.6);border:1px solid rgba(82,180,255,.15);border-radius:10px;margin-bottom:14px}
.entry h3{margin:0 0 8px;font-size:18px}
.entry h3 a{color:#fff;text-decoration:none}
.entry h3 a:hover{color:#52b4ff}
.entry .meta{font-family:'JetBrains Mono',monospace;font-size:11px;color:#7a92b0;letter-spacing:1px;margin-bottom:10px}
.entry .desc{color:#a8b8cc;font-size:14px;line-height:1.6}
</style>
</head>
<body>
<div class="starfield" aria-hidden="true"></div>
<div class="grid-bg" aria-hidden="true"></div>
<main class="feed-page">
<p style="font-family:'JetBrains Mono',monospace;font-size:11px;letter-spacing:2px;color:#52b4ff;margin-bottom:16px"><a href="/" style="color:inherit;text-decoration:none">← PURSUE Tracker</a> &#160;/&#160; RSS feed</p>
<h1><xsl:value-of select="title"/></h1>
<p class="lede"><xsl:value-of select="description"/></p>

<h2 style="color:#fff;margin:32px 0 8px">Subscribe in your reader</h2>
<p style="color:#a8b8cc;margin-bottom:14px">Click your reader to add this feed automatically, or copy the URL below:</p>
<div class="feed-url">https://pursueufotracker.com/generated/feed.xml</div>

<div class="reader-grid">
<a href="https://feedly.com/i/subscription/feed%2Fhttps%3A%2F%2Fpursueufotracker.com%2Fgenerated%2Ffeed.xml" target="_blank" rel="noopener">
<strong>Feedly</strong>One-click subscribe</a>
<a href="https://www.inoreader.com/?add_feed=https%3A%2F%2Fpursueufotracker.com%2Fgenerated%2Ffeed.xml" target="_blank" rel="noopener">
<strong>Inoreader</strong>One-click subscribe</a>
<a href="https://newsblur.com/?url=https%3A%2F%2Fpursueufotracker.com%2Fgenerated%2Ffeed.xml" target="_blank" rel="noopener">
<strong>NewsBlur</strong>Add to NewsBlur</a>
<a href="https://theoldreader.com/feeds/subscribe?url=https%3A%2F%2Fpursueufotracker.com%2Fgenerated%2Ffeed.xml" target="_blank" rel="noopener">
<strong>The Old Reader</strong>Subscribe</a>
</div>

<p style="color:#a8b8cc;font-size:14px;margin-bottom:32px">Don't have a reader? Try <a href="https://feedly.com" target="_blank" rel="noopener" style="color:#52b4ff">Feedly</a> (free, web + mobile), <a href="https://netnewswire.com" target="_blank" rel="noopener" style="color:#52b4ff">NetNewsWire</a> (macOS/iOS, free, open source), or your browser's built-in RSS support.</p>

<h2 style="color:#fff;margin:48px 0 16px">Latest entries (<xsl:value-of select="count(item)"/> total)</h2>
<xsl:for-each select="item">
<xsl:if test="position() &lt;= 15">
<div class="entry">
<h3><a href="{link}"><xsl:value-of select="title"/></a></h3>
<p class="meta"><xsl:value-of select="pubDate"/></p>
<p class="desc"><xsl:value-of select="substring(description, 1, 300)"/><xsl:if test="string-length(description) &gt; 300">&#8230;</xsl:if></p>
</div>
</xsl:if>
</xsl:for-each>

<p style="text-align:center;margin-top:48px"><a href="/" style="color:#52b4ff;font-family:'JetBrains Mono',monospace;font-size:13px;letter-spacing:1px;text-decoration:none">← BACK TO ALL FILES</a></p>
</main>
<footer style="text-align:center;padding:60px 24px;color:#7a92b0;font-size:13px;border-top:1px solid rgba(82,180,255,.1);margin-top:60px">
<p>Independent tracker. Not affiliated with the U.S. Department of War. <a href="/" style="color:#52b4ff">Back to tracker</a></p>
</footer>
</body>
</html>
</xsl:template>
</xsl:stylesheet>
