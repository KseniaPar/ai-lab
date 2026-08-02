package com.ailab.qa;

public final class CitationTimestamps {

    private CitationTimestamps() {
    }

    public static String format(Long startMs) {
        if (startMs == null) {
            return null;
        }
        long totalSec = startMs / 1000;
        long mm = totalSec / 60;
        long ss = totalSec % 60;
        return String.format("%d:%02d", mm, ss);
    }
}
