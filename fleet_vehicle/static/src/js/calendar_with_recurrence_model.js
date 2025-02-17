/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { CalendarWithRecurrenceModel } from "@maintenance/static/src/js/calendar_with_recurrence_model";

patch(CalendarWithRecurrenceModel.prototype, {
    async loadRecords(data) {
        const rawRecords = await this._super(data);  // Panggil method asli
        const records = {};
        let recordsCounter = 1;

        for (const rawRecord of rawRecords) {
            // Ambil semua log service name untuk request ini
            const logServiceNames = rawRecord.log_service_name ? rawRecord.log_service_name.split(", ") : [];

            // Ambil log service pertama untuk event utama
            const logServiceForMainEvent = logServiceNames.length > 0 ? logServiceNames[0] : "No Service";

            records[recordsCounter] = {
                ...this.normalizeRecord(rawRecord),
                id: recordsCounter,
                log_service_name: logServiceForMainEvent, // Event utama pakai service pertama
            };
            recordsCounter++;

            if (rawRecord.recurring_maintenance && !rawRecord.done && !rawRecord.archive) {
                let { start, end } = data.range;
                if (rawRecord.repeat_type == 'until') {
                    end = luxon.DateTime.min(end, deserializeDateTime(rawRecord.repeat_until)).endOf('day');
                }

                let date = deserializeDateTime(rawRecord.schedule_date);
                date = this._getNextDate(date, rawRecord.repeat_unit + 's', rawRecord.repeat_interval);
                let counter = 1;

                while (date <= end) {
                    if (date > start) {
                        const rawRecordCopy = { ...rawRecord };
                        rawRecordCopy.display_name = rawRecord.display_name + " (+" + counter + ")";
                        rawRecordCopy.schedule_date = serializeDateTime(date);

                        // Hanya ambil log_service jika masih dalam batas jumlah yang tersedia
                        const logServiceForThisIteration = logServiceNames[counter] || false;

                        records[recordsCounter] = {
                            ...this.normalizeRecord(rawRecordCopy),
                            id: recordsCounter,
                            isRecurrent: true,
                            log_service_name: logServiceForThisIteration, // Tidak mengulang jika habis
                        };
                        recordsCounter++;
                    }
                    date = this._getNextDate(date, rawRecord.repeat_unit + 's', rawRecord.repeat_interval);
                    counter++;

                    // Jika jumlah event lebih banyak dari log service yang tersedia, hentikan log service
                    if (counter >= logServiceNames.length) {
                        break;
                    }
                }
            }
        }
        return records;
    },

    _getNextDate(date, unit, interval) {
        return date.plus({ [unit]: interval });
    }
});
