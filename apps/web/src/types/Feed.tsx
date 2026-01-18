export interface PickerFilter {
    operation: string;
    args: string | string[];
}

export interface Picker {
    external_id: string;
    cronjob: string;
    source_url: string;
    filters: PickerFilter[];
    feed_external_id: string;
}

export interface FeedItem {
    external_id: string
    link: string
    author: string
    title: string
    created_at: string
    content?: string
    reading_time?: string
    image_url?: string
}

export interface Feed {
    name: string;
    external_id: string;
    created_at: string;
    pickers?: Picker[];
    feed_items?: FeedItem[]
    latest_item_datetime?: string,
    number_of_feed_items?: string
}
